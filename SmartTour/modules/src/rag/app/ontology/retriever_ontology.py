from .ontology_manager import OntologyManager
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from fuzzywuzzy import fuzz, process
from collections import defaultdict

# Descargar recursos necesarios de NLTK (ejecutar una vez)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class OntologyRetriever:
    def __init__(self, config):
        self.manager = OntologyManager(config["ontology"]["owl_path"])
        
        # Inicializar herramientas NLP
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))
        self.stop_words.update(['que', 'cual', 'donde', 'como', 'cuando', 'quien', 'hay', 'tiene', 'quiero', 'busco', 'necesito'])
        
        # Cargar modelo de spaCy para español (opcional, más preciso)
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except OSError:
            self.nlp = None
            print("Modelo spaCy español no encontrado. Usando NLTK básico.")
        
        # Diccionarios semánticos expandidos
        self.province_mapping = {
            # Nombres oficiales
            "habana": ["la habana", "havana", "capital", "ciudad habana"],
            "matanzas": ["varadero", "cardenas", "jovellanos"],
            "santiago de cuba": ["santiago", "oriente", "sierra maestra"],
            "holguin": ["guardalavaca", "banes", "gibara"],
            "guantanamo": ["baracoa", "guantánamo", "punta maisi"],
            "cienfuegos": ["jagua", "perla del sur"],
            "villa clara": ["santa clara", "caibarien", "remedios"],
            "sancti spiritus": ["trinidad", "topes collantes"],
            "ciego de avila": ["ciego", "moron", "jardines rey"],
            "camaguey": ["camagüey", "nuevitas", "santa lucia"],
            "granma": ["bayamo", "manzanillo", "pilón"],
            "las tunas": ["tunas", "puerto padre"],
            "pinar del rio": ["pinar", "viñales", "valle viñales", "maria la gorda"],
            "artemisa": ["san antonio banos", "bahia honda"],
            "mayabeque": ["san jose las lajas", "melena sur"]
        }
        
        self.place_type_synonyms = {
            "restaurante": ["restaurant", "paladar", "comedor", "cafeteria", "pizzeria", "bar", "taberna"],
            "hotel": ["hospedaje", "alojamiento", "hostal", "casa particular", "resort", "pension"],
            "museo": ["galeria", "exposicion", "centro cultural", "patrimonio", "monumento"],
            "playa": ["beach", "costa", "litoral", "balneario", "cayeria"],
            "teatro": ["cine", "auditorio", "sala espectaculos", "centro nocturno"],
            "parque": ["reserva", "area protegida", "jardin", "bosque", "natural"],
            "mercado": ["tienda", "shopping", "comercio", "bazar", "artesania"]
        }
        
        self.activity_synonyms = {
            "buceo": ["diving", "snorkel", "submarino", "arrecife"],
            "senderismo": ["trekking", "hiking", "caminar", "naturaleza"],
            "pesca": ["fishing", "deportiva", "altura"],
            "baile": ["danza", "salsa", "rumba", "son", "folklore"],
            "tour": ["excursion", "paseo", "recorrido", "visita", "guiada"],
            "cultura": ["arte", "historia", "tradicion", "patrimonio", "colonial"],
            "gastronomia": ["comida", "cocina", "culinario", "sabores"],
            "aventura": ["extremo", "adrenalina", "tirolesa", "escalada"]
        }
        
        # Inicializar vectorizador TF-IDF
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=list(self.stop_words),
            ngram_range=(1, 2),
            analyzer='word'
        )
        
        # Cache para búsquedas
        self.query_cache = {}

    def preprocess_query(self, query):
        """Preprocesa la consulta usando técnicas NLP avanzadas"""
        # Limpiar query
        query = query.lower().strip()
        
        # Usar spaCy si está disponible
        if self.nlp:
            doc = self.nlp(query)
            
            # Extraer entidades nombradas
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            # Extraer sustantivos, adjetivos y verbos importantes
            important_tokens = []
            for token in doc:
                if (not token.is_stop and not token.is_punct and 
                    token.pos_ in ['NOUN', 'ADJ', 'VERB', 'PROPN'] and 
                    len(token.text) > 2):
                    important_tokens.append(token.lemma_)
            
            return {
                'original': query,
                'entities': entities,
                'keywords': important_tokens,
                'cleaned': ' '.join(important_tokens)
            }
        else:
            # Fallback usando NLTK
            try:
                # Usar inglés para evitar el error de punkt_tab español
                tokens = word_tokenize(query, language='english')
            except LookupError:
                # Si falla, usar un split simple
                tokens = query.split()
            filtered_tokens = []
            
            for token in tokens:
                if (token.lower() not in self.stop_words and 
                    token.isalpha() and 
                    len(token) > 2):
                    stemmed = self.stemmer.stem(token.lower())
                    filtered_tokens.append(stemmed)
            
            return {
                'original': query,
                'entities': [],
                'keywords': filtered_tokens,
                'cleaned': ' '.join(filtered_tokens)
            }

    def extract_intent(self, query_data):
        """Extrae la intención de la consulta"""
        query = query_data['original']
        keywords = query_data['keywords']
        
        intents = {
            'search_place': ['buscar', 'encontrar', 'donde', 'ubicacion', 'lugar'],
            'recommendation': ['recomendar', 'sugerir', 'mejor', 'top', 'buenos'],
            'information': ['informacion', 'detalles', 'datos', 'sobre', 'que es'],
            'comparison': ['comparar', 'diferencia', 'mejor que', 'versus'],
            'activity': ['hacer', 'actividad', 'tour', 'visitar', 'experiencia'],
            'food': ['comer', 'comida', 'restaurante', 'gastronomia', 'cocina'],
            'accommodation': ['dormir', 'hotel', 'hospedaje', 'alojamiento']
        }
        
        intent_scores = {}
        for intent, intent_keywords in intents.items():
            score = 0
            for keyword in intent_keywords:
                if keyword in query:
                    score += 1
                # Usar fuzzy matching para palabras similares
                for kw in keywords:
                    if fuzz.ratio(keyword, kw) > 80:
                        score += 0.5
            intent_scores[intent] = score
        
        return max(intent_scores, key=intent_scores.get) if intent_scores else 'search_place'

    def fuzzy_match_province(self, query_keywords):
        """Encuentra provincias usando fuzzy matching"""
        best_matches = []
        
        for province, synonyms in self.province_mapping.items():
            all_terms = [province] + synonyms
            
            for term in all_terms:
                for keyword in query_keywords:
                    ratio = fuzz.ratio(term.lower(), keyword.lower())
                    if ratio > 70:  # Umbral de similitud
                        best_matches.append((province, ratio, term))
        
        # Ordenar por mejor coincidencia
        best_matches.sort(key=lambda x: x[1], reverse=True)
        return best_matches[0][0] if best_matches else None

    def semantic_search(self, query_data, search_type='all'):
        """Realiza búsqueda semántica usando diferentes estrategias"""
        results = []
        
        # 1. Búsqueda por provincia con fuzzy matching
        province = self.fuzzy_match_province(query_data['keywords'])
        if province:
            places = self.manager.search_places_by_province(province)
            results.extend([f"{p.name} ({province}): {p.desc}" for p in places[:3]])
        
        # 2. Búsqueda por tipo de lugar con sinónimos
        for place_type, synonyms in self.place_type_synonyms.items():
            if any(syn in query_data['original'] for syn in [place_type] + synonyms):
                places = self.manager.search_places_by_type(place_type)
                results.extend([f"{p.name} ({place_type.title()}): {p.desc}" for p in places[:2]])
                break
        
        # 3. Búsqueda por actividades con sinónimos
        for activity, synonyms in self.activity_synonyms.items():
            if any(syn in query_data['original'] for syn in [activity] + synonyms):
                places = self.manager.search_places_by_activity(activity)
                results.extend([f"{p.name}: {p.desc}" for p in places[:2]])
                break
        
        # 4. Búsqueda por palabras clave con TF-IDF
        if not results or len(results) < 3:
            keyword_results = self._tfidf_search(query_data['cleaned'])
            results.extend(keyword_results)
        
        return list(dict.fromkeys(results))[:5]  # Eliminar duplicados y limitar

    def _tfidf_search(self, query):
        """Búsqueda usando TF-IDF y similitud coseno"""
        try:
            # Obtener todas las descripciones de lugares
            all_places = self.manager.get_all_places()
            if not all_places:
                return []
            
            # Crear corpus de documentos
            documents = [f"{place.name} {place.desc}" for place in all_places]
            
            # Vectorizar documentos y query
            tfidf_matrix = self.vectorizer.fit_transform(documents + [query])
            
            # Calcular similitud coseno
            query_vector = tfidf_matrix[-1]
            doc_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(query_vector, doc_vectors).flatten()
            
            # Obtener mejores coincidencias
            best_indices = similarities.argsort()[-3:][::-1]
            
            results = []
            for idx in best_indices:
                if similarities[idx] > 0.1:  # Umbral mínimo de similitud
                    place = all_places[idx]
                    results.append(f"{place.name}: {place.desc}")
            
            return results
        except Exception as e:
            print(f"Error en búsqueda TF-IDF: {e}")
            return []

    def retrieve(self, query):
        """Método principal de recuperación mejorado"""
        # Cache de consultas
        if query in self.query_cache:
            return self.query_cache[query]
        
        # Preprocesar consulta
        query_data = self.preprocess_query(query)
        
        # Extraer intención
        intent = self.extract_intent(query_data)
        
        # Búsqueda semántica adaptada a la intención
        if intent == 'food':
            results = self._search_food_places(query_data)
        elif intent == 'accommodation':
            results = self._search_accommodation(query_data)
        elif intent == 'activity':
            results = self._search_activities(query_data)
        else:
            results = self.semantic_search(query_data)
        
        # Guardar en cache
        self.query_cache[query] = results
        
        return results

    def _search_food_places(self, query_data):
        """Búsqueda especializada para lugares de comida"""
        food_types = ['restaurante', 'paladar', 'cafeteria', 'bar']
        results = []
        
        for food_type in food_types:
            if food_type in query_data['original']:
                places = self.manager.search_places_by_type(food_type)
                results.extend([f"{p.name} ({food_type.title()}): {p.desc}" for p in places[:2]])
        
        if not results:
            # Búsqueda por cocina/gastronomía
            cuisine_keywords = ['cubana', 'italiana', 'china', 'internacional', 'criolla']
            for cuisine in cuisine_keywords:
                if cuisine in query_data['original']:
                    places = self.manager.search_places_by_cuisine(cuisine)
                    results.extend([f"{p.name}: {p.desc}" for p in places[:3]])
                    break
        
        return results

    def _search_accommodation(self, query_data):
        """Búsqueda especializada para alojamiento"""
        accommodation_types = ['hotel', 'casa particular', 'resort', 'hostal']
        results = []
        
        for acc_type in accommodation_types:
            if acc_type in query_data['original']:
                places = self.manager.search_places_by_type(acc_type)
                results.extend([f"{p.name}: {p.desc}" for p in places[:3]])
        
        return results

    def _search_activities(self, query_data):
        """Búsqueda especializada para actividades"""
        results = []
        
        # Buscar por actividades específicas
        for activity, synonyms in self.activity_synonyms.items():
            if any(syn in query_data['original'] for syn in [activity] + synonyms):
                places = self.manager.search_places_by_activity(activity)
                results.extend([f"{p.name} - {activity.title()}: {p.desc}" for p in places[:2]])
        
        return results

    def get_suggestions(self, partial_query):
        """Proporciona sugerencias de autocompletado"""
        suggestions = []
        
        # Sugerencias de provincias
        for province, synonyms in self.province_mapping.items():
            for term in [province] + synonyms:
                if partial_query.lower() in term.lower():
                    suggestions.append(f"Lugares en {province}")
        
        # Sugerencias de tipos de lugar
        for place_type, synonyms in self.place_type_synonyms.items():
            for term in [place_type] + synonyms:
                if partial_query.lower() in term.lower():
                    suggestions.append(f"{place_type.title()}s en Cuba")
        
        return suggestions[:5]
