from rdflib import Graph, Literal, RDF, RDFS, Namespace, URIRef
from rdflib.namespace import OWL, XSD
import os, json
from uuid import uuid4
import unicodedata
import re
from pathlib import Path
import pickle
from datetime import datetime

# Improved namespace following the pattern from rag_michell
EX = Namespace("http://smarttour.org/tourism#")

def clean_uri(value):
    """
    Improved URI cleaning function based on rag_michell implementation
    Removes accents, converts to ascii, removes quotes, parentheses, dots, commas, etc.
    """
    value = str(value or "")
    # Normalize and remove accents
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    # Keep only alphanumeric characters, spaces, and hyphens
    value = re.sub(r'[^\w\s-]', '', value)
    # Replace spaces and multiple underscores with single underscore
    value = value.replace(" ", "_").replace("__", "_")
    # Remove leading/trailing underscores and convert to lowercase
    value = value.strip("_").lower()
    return value if value else None

class OntologyBuilder:
    def __init__(self, store_file="data/tourism_ontology.ttl"):
        """
        Enhanced OntologyBuilder with improved initialization and SPARQL query capabilities
        """
        self.store_file = store_file
        self.graph = Graph()
        self.graph.bind("ex", EX)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
        
        # Enhanced caching for better performance
        self.provinces = set()
        self.cuisine_types = set()
        self.place_types = set()
        self.price_ranges = set()
        self.activities = set()
        self.contacts = set()
        
        # Statistics tracking
        self.stats = {
            'places_added': 0,
            'provinces_created': 0,
            'place_types_created': 0,
            'activities_created': 0
        }
        
        self._define_enhanced_schema()

    def _define_enhanced_schema(self):
        """
        Enhanced schema definition with improved structure and additional properties
        """
        # Main classes - following tourism domain best practices
        self.graph.add((EX.TouristPlace, RDF.type, OWL.Class))
        self.graph.add((EX.TouristPlace, RDFS.label, Literal("Tourist Place")))
        self.graph.add((EX.TouristPlace, RDFS.comment, Literal("A place of interest for tourists in Cuba")))
        
        self.graph.add((EX.Province, RDF.type, OWL.Class))
        self.graph.add((EX.Province, RDFS.label, Literal("Province")))
        
        self.graph.add((EX.CuisineType, RDF.type, OWL.Class))
        self.graph.add((EX.CuisineType, RDFS.label, Literal("Cuisine Type")))
        
        self.graph.add((EX.PlaceType, RDF.type, OWL.Class))
        self.graph.add((EX.PlaceType, RDFS.label, Literal("Place Type")))
        
        self.graph.add((EX.PriceRange, RDF.type, OWL.Class))
        self.graph.add((EX.PriceRange, RDFS.label, Literal("Price Range")))
        
        self.graph.add((EX.Contact, RDF.type, OWL.Class))
        self.graph.add((EX.Contact, RDFS.label, Literal("Contact Information")))
        
        self.graph.add((EX.Activity, RDF.type, OWL.Class))
        self.graph.add((EX.Activity, RDFS.label, Literal("Tourist Activity")))
        
        # Enhanced object properties with better semantics
        # Location properties
        self.graph.add((EX.locatedInProvince, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.locatedInProvince, RDFS.label, Literal("located in province")))
        self.graph.add((EX.estaEnProvincia, RDF.type, OWL.ObjectProperty))  # Spanish equivalent for compatibility
        self.graph.add((EX.estaEnProvincia, RDFS.label, Literal("está en provincia")))
        
        # Service and activity properties
        self.graph.add((EX.hasCuisineType, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasPlaceType, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasPriceRange, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasContact, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasActivity, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.ofreceActividad, RDF.type, OWL.ObjectProperty))  # Spanish equivalent for compatibility
        self.graph.add((EX.ofreceActividad, RDFS.label, Literal("ofrece actividad")))
        
        # Enhanced data properties
        self.graph.add((EX.hasName, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.tieneNombre, RDF.type, OWL.DatatypeProperty))  # Spanish equivalent
        self.graph.add((EX.tieneNombre, RDFS.label, Literal("tiene nombre")))
        
        self.graph.add((EX.hasDescription, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasAddress, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasPhone, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasEmail, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasUrl, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasRating, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasOpeningHours, RDF.type, OWL.DatatypeProperty))
        
        # Domain and range definitions for better SPARQL queries
        self._define_property_constraints()
    
    def _define_property_constraints(self):
        """Define domain and range constraints for properties"""
        # Location constraints
        self.graph.add((EX.locatedInProvince, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.locatedInProvince, RDFS.range, EX.Province))
        self.graph.add((EX.estaEnProvincia, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.estaEnProvincia, RDFS.range, EX.Province))
        
        # Service constraints
        self.graph.add((EX.hasCuisineType, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.hasCuisineType, RDFS.range, EX.CuisineType))
        self.graph.add((EX.hasPlaceType, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.hasPlaceType, RDFS.range, EX.PlaceType))
        self.graph.add((EX.hasPriceRange, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.hasPriceRange, RDFS.range, EX.PriceRange))
        self.graph.add((EX.hasContact, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.hasContact, RDFS.range, EX.Contact))
        self.graph.add((EX.hasActivity, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.hasActivity, RDFS.range, EX.Activity))
        self.graph.add((EX.ofreceActividad, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.ofreceActividad, RDFS.range, EX.Activity))
        
        # Data property constraints
        self.graph.add((EX.hasName, RDFS.domain, OWL.Thing))
        self.graph.add((EX.hasName, RDFS.range, XSD.string))
        self.graph.add((EX.tieneNombre, RDFS.domain, OWL.Thing))
        self.graph.add((EX.tieneNombre, RDFS.range, XSD.string))
        self.graph.add((EX.hasDescription, RDFS.domain, OWL.Thing))
        self.graph.add((EX.hasDescription, RDFS.range, XSD.string))
        self.graph.add((EX.hasAddress, RDFS.domain, OWL.Thing))
        self.graph.add((EX.hasAddress, RDFS.range, XSD.string))
        self.graph.add((EX.hasPhone, RDFS.domain, EX.Contact))
        self.graph.add((EX.hasPhone, RDFS.range, XSD.string))
        self.graph.add((EX.hasEmail, RDFS.domain, EX.Contact))
        self.graph.add((EX.hasEmail, RDFS.range, XSD.string))
        self.graph.add((EX.hasUrl, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.hasUrl, RDFS.range, XSD.string))
        self.graph.add((EX.hasRating, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.hasRating, RDFS.range, XSD.decimal))
        self.graph.add((EX.hasOpeningHours, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.hasOpeningHours, RDFS.range, XSD.string))

    def _get_or_create(self, name, cls, cache_set):
        """Enhanced resource creation with better URI handling"""
        safe_name = clean_uri(name)
        if not safe_name:
            return None
        
        # Create more semantic URIs
        class_name = cls.__name__.lower()
        uri = EX[f"{class_name}_{safe_name}"]
        
        if name not in cache_set:
            self.graph.add((uri, RDF.type, getattr(EX, cls.__name__)))
            self.graph.add((uri, RDFS.label, Literal(name)))
            # Add both English and Spanish name properties for compatibility
            self.graph.add((uri, EX.hasName, Literal(name)))
            self.graph.add((uri, EX.tieneNombre, Literal(name)))
            cache_set.add(name)
            
            # Update statistics
            if cls.__name__ == 'Province':
                self.stats['provinces_created'] += 1
            elif cls.__name__ == 'PlaceType':
                self.stats['place_types_created'] += 1
            elif cls.__name__ == 'Activity':
                self.stats['activities_created'] += 1
        
        return uri

    def _get_or_create_province(self, province_name):
        return self._get_or_create(province_name, Province, self.provinces)

    def _get_or_create_cuisine(self, cuisine_name):
        return self._get_or_create(cuisine_name, CuisineType, self.cuisine_types)

    def _get_or_create_place_type(self, place_type_name):
        return self._get_or_create(place_type_name, PlaceType, self.place_types)

    def _get_or_create_price_range(self, price_range):
        return self._get_or_create(price_range, PriceRange, self.price_ranges)

    def _get_or_create_activity(self, activity_name):
        return self._get_or_create(activity_name, Activity, self.activities)

    def _create_contact(self, phones, emails):
        contact_uri = EX["contact_" + str(uuid4())]
        self.graph.add((contact_uri, RDF.type, EX.Contact))
        for phone in phones:
            self.graph.add((contact_uri, EX.hasPhone, Literal(phone)))
        for email in emails:
            self.graph.add((contact_uri, EX.hasEmail, Literal(email)))
        return contact_uri

    def add_place(self, name, province, cuisine_types, description, price_range=None, place_types=None, address=None, url=None, phones=None, emails=None, activities=None, rating=None, opening_hours=None):
        """Enhanced place addition with better data handling"""
        place_uri = EX[f"place_{clean_uri(name)}_{str(uuid4())[:8]}"]
        self.graph.add((place_uri, RDF.type, EX.TouristPlace))
        
        # Add names in both English and Spanish properties
        self.graph.add((place_uri, EX.hasName, Literal(name)))
        self.graph.add((place_uri, EX.tieneNombre, Literal(name)))
        self.graph.add((place_uri, EX.hasDescription, Literal(description)))
        
        # Optional properties
        if address:
            self.graph.add((place_uri, EX.hasAddress, Literal(address)))
        if url:
            self.graph.add((place_uri, EX.hasUrl, Literal(url)))
        if rating:
            self.graph.add((place_uri, EX.hasRating, Literal(float(rating))))
        if opening_hours:
            self.graph.add((place_uri, EX.hasOpeningHours, Literal(opening_hours)))
        
        # Province relationship (both English and Spanish properties for compatibility)
        if province:
            prov_uri = self._get_or_create_province(province)
            if prov_uri:
                self.graph.add((place_uri, EX.locatedInProvince, prov_uri))
                self.graph.add((place_uri, EX.estaEnProvincia, prov_uri))
        
        # Cuisine types
        for cuisine in filter(None, cuisine_types or []):
            cuisine_uri = self._get_or_create_cuisine(cuisine)
            if cuisine_uri:
                self.graph.add((place_uri, EX.hasCuisineType, cuisine_uri))
        
        # Place types
        for pt in filter(None, place_types or []):
            pt_uri = self._get_or_create_place_type(pt)
            if pt_uri:
                self.graph.add((place_uri, EX.hasPlaceType, pt_uri))
        
        # Price range
        if price_range:
            pr_uri = self._get_or_create_price_range(price_range)
            if pr_uri:
                self.graph.add((place_uri, EX.hasPriceRange, pr_uri))
        
        # Contact information
        if (phones or emails):
            contact_uri = self._create_contact(phones or [], emails or [])
            self.graph.add((place_uri, EX.hasContact, contact_uri))
        
        # Activities (both English and Spanish properties for compatibility)
        for act in filter(None, activities or []):
            act_uri = self._get_or_create_activity(act)
            if act_uri:
                self.graph.add((place_uri, EX.hasActivity, act_uri))
                self.graph.add((place_uri, EX.ofreceActividad, act_uri))
        
        # Update statistics
        self.stats['places_added'] += 1
        
        return place_uri

    def parse_jsonl_file(self, jsonl_path):
        """Procesa un archivo JSONL (JSON Lines) donde cada línea es un objeto JSON"""
        try:
            line_count = 0
            processed_count = 0
            
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # Saltar líneas vacías
                        continue
                    
                    line_count += 1
                    try:
                        data = json.loads(line)
                        if self._parse_json_data(data, f"línea {line_num}"):
                            processed_count += 1
                    except json.JSONDecodeError as e:
                        print(f"Error al parsear JSON en línea {line_num}: {e}")
                    except Exception as e:
                        print(f"Error procesando línea {line_num}: {e}")
            
            print(f"Procesamiento completado: {processed_count}/{line_count} entradas procesadas exitosamente")
                        
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {jsonl_path}")
        except Exception as e:
            print(f"Error al abrir el archivo {jsonl_path}: {e}")

    def parse_json_folder(self, folder_path):
        """Mantiene compatibilidad con el método anterior para procesar carpetas de JSON"""
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".json"):
                    self._parse_file(os.path.join(root, file))

    def _parse_file(self, path):
        """Procesa un archivo JSON individual (mantiene compatibilidad)"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._parse_json_data(data, path)
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON en {path}: {e}")
        except Exception as e:
            print(f"Error procesando archivo {path}: {e}")

    def _parse_json_data(self, data, source_identifier):
        """Procesa un objeto JSON individual (ya sea de archivo .json o línea .jsonl)"""
        try:
            # Verificar que data no sea None y sea un diccionario
            if not isinstance(data, dict):
                print(f"Fuente {source_identifier} no contiene un diccionario válido, saltando...")
                return False

            # --------- OBTENER EL NOMBRE DEL LUGAR SOLO DEL CAMPO 'titulo' ---------
            nombre = ""
            if "titulo" in data and isinstance(data["titulo"], str):
                nombre = data["titulo"].strip()
            
            # Verificar si es contenido general/informativo que no debe procesarse
            url = data.get("url", "")
            if self._is_general_content(nombre, url):
                print(f"Contenido general detectado en {source_identifier}, saltando...")
                return False
            
            # Si no hay nombre válido, intentar extraer de URL o saltar
            if not nombre or nombre in ["", "503 Service Temporarily Unavailable", "Perfil"]:
                if url:
                    # Intentar extraer nombre del final de la URL
                    nombre = url.split("/")[-2] if url.endswith("/") else url.split("/")[-1]
                    nombre = nombre.replace("-", " ").replace("_", " ").title()
                if not nombre or len(nombre) < 3:
                    print(f"Fuente {source_identifier} no tiene campo 'titulo' válido, saltando...")
                    return False
            # ---------------------------------------------------------------

            # Extraer contenido de secciones de manera más inteligente
            secciones = data.get("secciones", [])
            if not isinstance(secciones, list):
                secciones = []
            
            all_fragments = []
            structured_content = {}
            
            for seccion in secciones:
                if not isinstance(seccion, dict):
                    continue
                titulo_seccion = seccion.get("titulo", "") or ""
                titulo_seccion = titulo_seccion.lower()
                fragmentos = seccion.get("fragmentos", [])
                if not isinstance(fragmentos, list):
                    fragmentos = []
                fragmentos = [f for f in fragmentos if isinstance(f, str)]
                # Organizar fragmentos por tipo de sección
                if any(keyword in titulo_seccion for keyword in ["descripcion", "sobre", "acerca", "historia", "caracteristicas"]):
                    structured_content["description"] = " ".join(fragmentos)
                elif any(keyword in titulo_seccion for keyword in ["ubicacion", "direccion", "donde", "localizado"]):
                    structured_content["location"] = " ".join(fragmentos)
                elif any(keyword in titulo_seccion for keyword in ["servicios", "facilidades", "ofertas", "actividades"]):
                    structured_content["services"] = fragmentos
                elif any(keyword in titulo_seccion for keyword in ["horario", "horarios", "cuando", "abierto"]):
                    structured_content["schedule"] = " ".join(fragmentos)
                elif any(keyword in titulo_seccion for keyword in ["contacto", "telefono", "email", "comunicacion"]):
                    structured_content["contact"] = " ".join(fragmentos)
                all_fragments.extend(fragmentos)
            
            # Solo procesar si tenemos información mínima
            if not nombre or not all_fragments:
                print(f"Fuente {source_identifier} no contiene información suficiente, saltando...")
                return False
            
            provincia = self._extract_province(all_fragments, structured_content.get("location", ""))
            cocina = self._extract_cuisine_types(all_fragments)
            place_types = self._extract_place_types(all_fragments, nombre)
            activities = self._extract_activities(all_fragments, structured_content.get("services", []))
            descripcion = self._create_useful_description(
                nombre, 
                structured_content.get("description", ""),
                all_fragments,
                provincia,
                place_types
            )
            phones = self._extract_phones(all_fragments)
            emails = self._extract_emails(all_fragments)
            address = self._extract_address(all_fragments, structured_content.get("location", ""))
            precio = self._extract_price_range(all_fragments)
            url = data.get("url")

            # Solo agregar si tenemos información útil y nombre válido
            if provincia and descripcion and len(descripcion) > 50 and nombre:
                # Verificación adicional para asegurar que es un lugar turístico específico
                if self._is_valid_tourist_place(nombre, all_fragments, place_types):
                    self.add_place(
                        nombre, provincia, cocina, descripcion, precio,
                        place_types=place_types if place_types else None, address=address, url=url,
                        phones=phones, emails=emails, activities=activities
                    )
                    return True
                else:
                    print(f"'{nombre}' parece ser contenido general, no un lugar turístico específico")
                    return False
            else:
                print(f"Lugar '{nombre}' no tiene información suficiente para ser agregado")
                return False
                
        except Exception as e:
            print(f"Error procesando datos de {source_identifier}: {e}")
            return False

    def _is_general_content(self, title, url):
        """Detecta si el contenido es información general sobre Cuba y no un lugar específico"""
        if not title and not url:
            return True
            
        # Patrones en títulos que indican contenido general
        general_title_patterns = [
            "naturaleza de", "eventos en cuba", "sobre cuba", "geografía", "historia de",
            "cultura de", "tradiciones de", "música de", "gastronomía de", "arte de",
            "clima de", "sociedad", "escenario cultural", "literatura", "danza",
            "teatro", "arquitectura", "religión", "costumbres", "el cubano",
            "cultivo del tabaco", "ron", "café", "comida típica", "blog",
            "información general", "guía de", "todo sobre", "conoce cuba",
            "descubre cuba", "cuba travel", "turismo en cuba"
        ]
        
        # Patrones en URLs que indican contenido general
        general_url_patterns = [
            "/naturaleza", "/geografia", "/historia", "/cultura", "/tradiciones",
            "/musica", "/gastronomia", "/arte", "/clima", "/sociedad", "/blog",
            "/eventos", "/informacion", "/guia", "/sobre", "/acerca", "/conoce",
            "/descubre", "/general"
        ]
        
        if title:
            title_lower = title.lower()
            for pattern in general_title_patterns:
                if pattern in title_lower:
                    return True
        
        if url:
            url_lower = url.lower()
            for pattern in general_url_patterns:
                if pattern in url_lower:
                    return True
                    
        return False

    def _is_valid_tourist_place(self, nombre, all_fragments, place_types):
        """Verifica si realmente es un lugar turístico específico y no contenido general"""
        
        # Verificar si tiene características de lugar específico
        specific_indicators = [
            "dirección", "direccion", "ubicado en", "situada en", "localizado en",
            "teléfono", "telefono", "email", "horario", "abierto", "cerrado",
            "precio", "costo", "tarifa", "menú", "menu", "especialidad",
            "reservas", "reservaciones", "contacto"
        ]
        
        # Verificar si el contenido contiene principalmente información general
        general_content_indicators = [
            "sobre", "geografía", "geografia", "naturaleza", "clima", "sociedad",
            "historia", "escenario cultural", "música", "musica", "cine", 
            "literatura", "artes visuales", "danza", "teatro", "arquitectura",
            "tradiciones", "costumbres", "el cubano", "cultivo del tabaco",
            "ron", "café", "cafe", "religión", "religion", "comida típica",
            "primeros pobladores", "encuentro de dos mundos", "la colonia",
            "la república", "periodo revolucionario"
        ]
        
        all_text = (nombre + " " + " ".join(all_fragments)).lower()
        
        # Contar indicadores específicos vs generales
        specific_count = sum(1 for indicator in specific_indicators if indicator in all_text)
        general_count = sum(1 for indicator in general_content_indicators if indicator in all_text)
        
        # Si hay más contenido general que específico, probablemente no es un lugar turístico
        if general_count > specific_count and general_count > 3:
            return False
            
        # Si no tiene tipos de lugar identificables y tiene mucho contenido general
        if not place_types and general_count > 2:
            return False
            
        # Verificar longitud de fragmentos - contenido general tiende a tener fragmentos muy largos con listas
        very_long_fragments = [f for f in all_fragments if len(f) > 200]
        if len(very_long_fragments) > 0:
            # Si tiene fragmentos muy largos con contenido general, probablemente no es un lugar específico
            for fragment in very_long_fragments:
                fragment_lower = fragment.lower()
                general_in_fragment = sum(1 for indicator in general_content_indicators if indicator in fragment_lower)
                if general_in_fragment > 5:
                    return False
        
        return True

    def _extract_province(self, fragments, location_text):
        """Extrae la provincia de manera más precisa"""
        provinces_mapping = {
            "villa clara": ["villa clara", "santa clara", "remedios", "caibarien", "sagua"],
            "la habana": ["habana", "havana", "capital", "vedado", "miramar", "centro habana"],
            "matanzas": ["matanzas", "varadero", "cardenas", "jovellanos"],
            "santiago de cuba": ["santiago", "santiago de cuba"],
            "holguin": ["holguin", "holguín", "guardalavaca", "banes"],
            "guantanamo": ["guantanamo", "guantánamo", "baracoa"],
            "cienfuegos": ["cienfuegos", "jagua"],
            "sancti spiritus": ["sancti spiritus", "trinidad", "topes"],
            "ciego de avila": ["ciego", "ciego de avila", "moron"],
            "camaguey": ["camaguey", "camagüey"],
            "granma": ["granma", "bayamo", "manzanillo"],
            "las tunas": ["las tunas", "tunas"],
            "pinar del rio": ["pinar", "pinar del rio", "viñales", "vinales"],
            "artemisa": ["artemisa", "san antonio"],
            "mayabeque": ["mayabeque", "san jose"]
        }
        
        search_text = (location_text + " " + " ".join(fragments)).lower()
        
        for province, keywords in provinces_mapping.items():
            for keyword in keywords:
                if keyword in search_text:
                    return province.title()
        
        # Buscar patrones específicos
        for fragment in fragments:
            fragment_lower = fragment.lower()
            if fragment_lower.startswith("provincia"):
                parts = fragment.split(":")
                if len(parts) > 1:
                    return parts[1].strip().title()
            
            if "ubicado en" in fragment_lower or "situada en" in fragment_lower:
                for province, keywords in provinces_mapping.items():
                    for keyword in keywords:
                        if keyword in fragment_lower:
                            return province.title()
        
        return "Cuba"  # Default fallback

    def _extract_cuisine_types(self, fragments):
        """Extrae tipos de cocina de manera más precisa"""
        cuisine_keywords = {
            "cubana": ["cubana", "criolla", "tradicional cubana"],
            "internacional": ["internacional", "variada", "fusion"],
            "italiana": ["italiana", "pizza", "pasta"],
            "china": ["china", "chino", "oriental"],
            "española": ["española", "ibérica"],
            "francesa": ["francesa", "gourmet"],
            "mexicana": ["mexicana", "tacos"],
            "vegetariana": ["vegetariana", "vegana", "vegetarian"],
            "mariscos": ["mariscos", "pescado", "seafood"],
            "parrilla": ["parrilla", "asados", "barbacoa", "grill"]
        }
        
        found_cuisines = []
        search_text = " ".join(fragments).lower()
        
        for cuisine, keywords in cuisine_keywords.items():
            for keyword in keywords:
                if keyword in search_text:
                    found_cuisines.append(cuisine)
                    break
        
        return found_cuisines

    def _extract_place_types(self, fragments, name):
        """Extrae tipos de lugar de manera más precisa"""
        place_keywords = {
            "restaurante": ["restaurante", "paladar", "comedor"],
            "hotel": ["hotel", "casa particular", "hospedaje", "alojamiento"],
            "museo": ["museo", "galería", "exposición"],
            "playa": ["playa", "balneario", "costa"],
            "teatro": ["teatro", "cine", "auditorio"],
            "parque": ["parque", "reserva", "área protegida"],
            "bar": ["bar", "cafetería", "café"],
            "tienda": ["tienda", "shop", "comercio"],
            "centro cultural": ["centro cultural", "casa de cultura"],
            "iglesia": ["iglesia", "catedral", "templo"],
            "fortaleza": ["fortaleza", "castillo", "fuerte"],
            "plaza": ["plaza", "parque central"],
            "mercado": ["mercado", "bazar"]
        }
        
        found_types = []
        search_text = (name + " " + " ".join(fragments)).lower()
        
        for place_type, keywords in place_keywords.items():
            for keyword in keywords:
                if keyword in search_text:
                    found_types.append(place_type)
                    break
        
        return found_types

    def _extract_activities(self, fragments, services):
        """Extrae actividades disponibles"""
        activity_keywords = [
            "buceo", "snorkel", "pesca", "natación", "windsurf", "kayak",
            "senderismo", "trekking", "escalada", "ciclismo",
            "baile", "salsa", "música", "espectáculo",
            "tour", "excursión", "visita guiada",
            "golf", "tenis", "voleibol",
            "spa", "masajes", "relajación",
            "compras", "shopping",
            "fotografía", "avistamiento"
        ]
        
        found_activities = []
        search_text = " ".join(fragments + services).lower()
        
        for activity in activity_keywords:
            if activity in search_text:
                found_activities.append(activity)
        
        return found_activities

    def _create_useful_description(self, name, main_description, fragments, province, place_types):
        """Crea una descripción más útil y específica"""
        description_parts = []
        
        # Solo agregar tipo si es válido y específico
        if place_types and len(place_types) > 0:
            # Evitar clasificaciones genéricas incorrectas
            valid_place_types = [pt for pt in place_types if pt not in ["lugar", "sitio", "destino"]]
            if valid_place_types:
                description_parts.append(f"{name} es un {valid_place_types[0]} ubicado en {province}.")
            else:
                description_parts.append(f"{name} es un lugar turístico en {province}.")
        else:
            description_parts.append(f"{name} es un lugar turístico en {province}.")
            
        # Usar la descripción principal si existe y es útil
        if main_description and len(main_description) > 50:
            # Filtrar descripciones que contienen principalmente contenido general
            general_keywords = ["sobre", "geografía", "naturaleza", "clima", "sociedad", "historia", 
                              "escenario cultural", "música", "literatura", "tradiciones"]
            general_count = sum(1 for keyword in general_keywords if keyword.lower() in main_description.lower())
            
            if general_count < 3 and not any(generic in main_description.lower() for generic in 
                      ["información útil", "¿cómo llegar?", "horario y festividades", 
                       "comunicaciones", "servicios bancarios", "ofertas"]):
                description_parts.append(main_description)
                
        # Buscar fragmentos descriptivos útiles y específicos
        for fragment in fragments:
            if (len(fragment) > 50 and len(fragment) < 300 and 
                not any(generic in fragment.lower() for generic in 
                       ["información útil", "¿cómo llegar?", "horario", "comunicaciones", 
                        "servicios bancarios", "ofertas", "festividades", "sobre cuba",
                        "geografía", "naturaleza", "clima", "sociedad", "historia"]) and
                not fragment.startswith("Zona ") and
                not fragment.startswith("Tipo de") and
                not "escenario cultural" in fragment.lower() and
                not "tradiciones" in fragment.lower()):
                description_parts.append(fragment)
                break
                
        # Si no tenemos descripción útil, crear una básica
        if len(description_parts) == 1:
            description_parts.append(f"Un destino turístico recomendado para visitar en {province}, Cuba.")
            
        return " ".join(description_parts)

    def _extract_phones(self, fragments):
        """Extrae números de teléfono"""
        phones = []
        phone_pattern = r'[\+]?[\d\s\-\(\)]{8,}'
        
        for fragment in fragments:
            if any(keyword in fragment.lower() for keyword in ["teléfono", "telefono", "tel", "phone"]):
                found_phones = re.findall(phone_pattern, fragment)
                phones.extend([phone.strip() for phone in found_phones])
        
        return phones

    def _extract_emails(self, fragments):
        """Extrae direcciones de email"""
        emails = []
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-ZaZ0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        for fragment in fragments:
            found_emails = re.findall(email_pattern, fragment)
            emails.extend(found_emails)
        
        return emails

    def _extract_address(self, fragments, location_text):
        """Extrae dirección específica"""
        for fragment in fragments:
            if any(keyword in fragment.lower() for keyword in ["dirección", "direccion", "ubicado en", "situada en"]):
                if ":" in fragment:
                    return fragment.split(":", 1)[1].strip()
                else:
                    return fragment.strip()
        
        if location_text and len(location_text) > 10:
            return location_text
        
        return None

    def _extract_price_range(self, fragments):
        """Extrae rango de precios"""
        price_keywords = ["precio", "costo", "tarifa", "rango de precios"]
        
        for fragment in fragments:
            fragment_lower = fragment.lower()
            if any(keyword in fragment_lower for keyword in price_keywords):
                if ":" in fragment:
                    return fragment.split(":", 1)[1].strip()
                else:
                    # Buscar patrones de precio
                    if any(symbol in fragment for symbol in ["$", "€", "CUC", "CUP", "USD"]):
                        return fragment.strip()
        
        return None

    def save(self, filepath=None, format="ttl"):
        """Enhanced save method with multiple format support"""
        if filepath is None:
            filepath = self.store_file
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            if format == "ttl":
                self.graph.serialize(destination=filepath, format="turtle")
            elif format == "xml" or format == "owl":
                self.graph.serialize(destination=filepath, format="xml")
            elif format == "n3":
                self.graph.serialize(destination=filepath, format="n3")
            else:
                self.graph.serialize(destination=filepath, format=format)
            
            print(f"✅ Ontology saved to {filepath} in {format} format")
            print(f"📊 Statistics: {self.get_statistics()}")
            return True
        except Exception as e:
            print(f"❌ Error saving ontology: {e}")
            return False

    def get_statistics(self):
        """Get ontology statistics"""
        total_triples = len(self.graph)
        
        # Count instances by type
        sparql_counts = {
            'places': """
                PREFIX ex: <http://smarttour.org/tourism#>
                SELECT (COUNT(?place) as ?count) WHERE {
                    ?place a ex:TouristPlace .
                }
            """,
            'provinces': """
                PREFIX ex: <http://smarttour.org/tourism#>
                SELECT (COUNT(?prov) as ?count) WHERE {
                    ?prov a ex:Province .
                }
            """,
            'activities': """
                PREFIX ex: <http://smarttour.org/tourism#>
                SELECT (COUNT(?act) as ?count) WHERE {
                    ?act a ex:Activity .
                }
            """,
            'place_types': """
                PREFIX ex: <http://smarttour.org/tourism#>
                SELECT (COUNT(?type) as ?count) WHERE {
                    ?type a ex:PlaceType .
                }
            """
        }
        
        stats = {'total_triples': total_triples}
        for key, query in sparql_counts.items():
            try:
                result = list(self.query_ontology(query))
                stats[key] = int(result[0][0]) if result else 0
            except:
                stats[key] = 0
        
        return stats

    def query_ontology(self, sparql_query):
        """Execute SPARQL query on the ontology"""
        try:
            return self.graph.query(sparql_query)
        except Exception as e:
            print(f"Error executing SPARQL query: {e}")
            return []

# Enhanced auxiliary classes for better type checking
class Province: pass
class CuisineType: pass
class PlaceType: pass
class PriceRange: pass
class Activity: pass

# SPARQL Query Capabilities - Enhanced from rag_michell implementation

@staticmethod
def extract_entity(query):
    """Extract province or location entity from query"""
    patterns = [
        r"(en|de)\s+([A-Za-zÁÉÍÓÚÑáéíóúñ ]+)",
        r"(provincia|municipio)\s+([A-Za-zÁÉÍÓÚÑáéíóúñ ]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            entity = match.group(2).strip()
            return entity
    return None

@staticmethod
def is_structured_query(query):
    """Detect if query is structured for ontology usage"""
    patterns = [
        r"(actividades|lugares|hoteles|restaurantes).*(en|de)\s+([A-Za-zÁÉÍÓÚÑáéíóúñ ]+)",
        r"(qué|que).*(actividades|lugares).*(en|de)\s+([A-Za-zÁÉÍÓÚÑáéíóúñ ]+)",
        r"(municipio|provincia)\s+([A-Za-zÁÉÍÓÚÑáéíóúñ ]+)",
        r"(where|donde).*(can|puedo).*(visit|visitar)",
        r"(what|que).*(do|hacer).*(in|en)",
        r"(recommend|recomienda).*(places|lugares).*(in|en)"
    ]
    
    for pattern in patterns:
        if re.search(pattern, query.lower()):
            return True
    return False

def build_sparql_query(self, query, entity):
    """Build SPARQL query based on query type and entity"""
    normalized_entity = self.normalize_province_name(entity) if entity else entity
    
    if any(keyword in query.lower() for keyword in ["actividades", "activities", "que hacer", "what to do"]):
        return f"""
        PREFIX ex: <http://smarttour.org/tourism#>
        SELECT DISTINCT ?actividad WHERE {{

            ?lugar a ex:TouristPlace ;
                ex:ofreceActividad ?activity ;
                ex:estaEnProvincia ?provincia .

            ?activity ex:tieneNombre ?actividad .
            ?provincia ex:tieneNombre "{normalized_entity}" .
        }}
        """
    
    elif any(keyword in query.lower() for keyword in ["lugares", "places", "visitar", "visit", "hoteles", "hotels", "restaurantes", "restaurants"]):
        return f"""
        PREFIX ex: <http://smarttour.org/tourism#>
        SELECT DISTINCT ?nombre_lugar ?tipo_lugar WHERE {{
            ?lugar a ex:TouristPlace ;
                ex:tieneNombre ?nombre_lugar ;
                ex:estaEnProvincia ?provincia .
            ?provincia ex:tieneNombre "{normalized_entity}" .

            OPTIONAL {{
                ?lugar ex:hasPlaceType ?tipo .
                ?tipo ex:tieneNombre ?tipo_lugar .
            }}
        }}
        """
    
    elif any(keyword in query.lower() for keyword in ["cocina", "cuisine", "comida", "food"]):
        return f"""
        PREFIX ex: <http://smarttour.org/tourism#>
        SELECT DISTINCT ?nombre_lugar ?cocina WHERE {{
            ?lugar a ex:TouristPlace ;
                ex:tieneNombre ?nombre_lugar ;
                ex:estaEnProvincia ?provincia ;
                ex:hasCuisineType ?cuisine .
            ?provincia ex:tieneNombre "{normalized_entity}" .
            ?cuisine ex:tieneNombre ?cocina .
        }}
        """
    
    return None

def query_ontology(self, sparql_query):
    """Execute SPARQL query on the ontology"""
    try:
        return self.graph.query(sparql_query)
    except Exception as e:
        print(f"Error executing SPARQL query: {e}")
        return []

def get_structured_answer(self, query):
    """Get structured answer from ontology for supported queries"""
    if not self.is_structured_query(query):
        return None
    
    entity = self.extract_entity(query)
    if not entity:
        return None
    
    sparql = self.build_sparql_query(query, entity)
    if not sparql:
        return None
    
    try:
        results = self.query_ontology(sparql)
        result_list = []
        for row in results:
            if len(row) == 1:
                result_list.append(str(row[0]))
            else:
                result_list.append(" - ".join(str(cell) for cell in row))
        return result_list
    except Exception as e:
        print(f"Error executing structured query: {e}")
        return None

def get_all_provinces(self):
    """Get all provinces in the ontology"""
    provinces = []
    sparql = """
    PREFIX ex: <http://smarttour.org/tourism#>
    SELECT DISTINCT ?nombre WHERE {
        ?provincia a ex:Province ;
                    ex:tieneNombre ?nombre .
    }
    """
    results = self.query_ontology(sparql)
    for row in results:
        provinces.append(str(row[0]))
    return provinces

def normalize_province_name(self, entity):
    """Normalize province name for better matching"""
    available_provinces = self.get_all_provinces()
    
    # Exact match (case insensitive)
    for prov in available_provinces:
        if entity.lower() == prov.lower():
            return prov
    
    # Partial match
    for prov in available_provinces:
        if entity.lower() in prov.lower() or prov.lower() in entity.lower():
            return prov
    
    return entity

# Enhanced Ontology Management Methods

def load_ontology(self):
    """Load ontology from file"""
    if os.path.exists(self.store_file):
        try:
            self.graph.parse(self.store_file, format="ttl")
            print(f"✅ Ontology loaded from {self.store_file}")
            return True
        except Exception as e:
            print(f"❌ Error loading ontology: {e}")
            return False
    else:
        print(f"⚠️ Ontology file {self.store_file} not found, starting with empty ontology")
        return False
