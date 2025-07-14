from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
from rdflib.namespace import XSD
import os
import json
import re
import unicodedata
from uuid import uuid4

EX = Namespace("http://smarttour.org/tourism#")

def normalize_text(text):
    text = str(text or "")
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text)
    text = text.replace(" ", "_").replace("__", "_")
    return text.strip("_").lower()

class OntologyBuilder:
    def __init__(self):
        self.graph = Graph()
        self.graph.bind("ex", EX)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
        self.province_map = {
            "la habana": ["habana", "havana", "capital", "vedado", "miramar", "centro habana"],
            "matanzas": ["matanzas", "varadero", "cardenas", "jovellanos"],
            "villa clara": ["villa clara", "santa clara", "remedios", "caibarien", "sagua"],
            "santiago de cuba": ["santiago", "santiago de cuba", "oriente"],
            "holguin": ["holguin", "holguín", "guardalavaca", "banes", "gibara"],
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
        self.place_types = {
            "restaurante": ["restaurante", "paladar", "comedor", "cafeteria", "pizzeria", "bar"],
            "hotel": ["hotel", "casa particular", "hospedaje", "alojamiento", "hostal", "resort"],
            "museo": ["museo", "galeria", "exposicion", "centro cultural", "monumento"],
            "playa": ["playa", "balneario", "costa", "beach"],
            "teatro": ["teatro", "cine", "auditorio"],
            "parque": ["parque", "reserva", "jardin", "bosque", "natural"],
            "mercado": ["mercado", "tienda", "shopping", "comercio", "bazar", "artesania"]
        }
        self.cuisine_types = {
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
        self.activity_types = [
            "buceo", "snorkel", "pesca", "natación", "windsurf", "kayak",
            "senderismo", "trekking", "escalada", "ciclismo",
            "baile", "salsa", "música", "espectáculo",
            "tour", "excursión", "visita guiada",
            "golf", "tenis", "voleibol",
            "spa", "masajes", "relajación",
            "compras", "shopping",
            "fotografía", "avistamiento"
        ]
        self._define_schema()
        self._cache = {
            "province": {},
            "place_type": {},
            "cuisine": {},
            "activity": {},
            "price_range": {},
            "contact": {}
        }

    def _define_schema(self):
        # Clases
        self.graph.add((EX.TouristPlace, RDF.type, OWL.Class))
        self.graph.add((EX.Province, RDF.type, OWL.Class))
        self.graph.add((EX.PlaceType, RDF.type, OWL.Class))
        self.graph.add((EX.CuisineType, RDF.type, OWL.Class))
        self.graph.add((EX.Activity, RDF.type, OWL.Class))
        self.graph.add((EX.PriceRange, RDF.type, OWL.Class))
        self.graph.add((EX.Contact, RDF.type, OWL.Class))
        # Object properties
        self.graph.add((EX.locatedInProvince, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasPlaceType, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasCuisineType, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasActivity, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasPriceRange, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasContact, RDF.type, OWL.ObjectProperty))
        # Data properties
        self.graph.add((EX.hasName, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasDescription, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasAddress, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasUrl, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasPhone, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasEmail, RDF.type, OWL.DatatypeProperty))
        # Ranges/domains (opcional, pero recomendable)
        self.graph.add((EX.locatedInProvince, RDFS.domain, EX.TouristPlace))
        self.graph.add((EX.locatedInProvince, RDFS.range, EX.Province))
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
        self.graph.add((EX.hasName, RDFS.domain, OWL.Thing))
        self.graph.add((EX.hasName, RDFS.range, XSD.string))
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

    def _get_or_create(self, label, cls, cache_key):
        label_norm = normalize_text(label)
        if not label_norm:
            return None
        if label_norm in self._cache[cache_key]:
            return self._cache[cache_key][label_norm]
        uri = EX[f"{cache_key}_{label_norm}"]
        self.graph.add((uri, RDF.type, getattr(EX, cls)))
        self.graph.add((uri, RDFS.label, Literal(label)))
        self._cache[cache_key][label_norm] = uri
        return uri

    def _extract_province(self, text):
        text = text.lower()
        for prov, synonyms in self.province_map.items():
            if prov in text:
                return prov.title()
            for syn in synonyms:
                if syn in text:
                    return prov.title()
        return "Cuba"

    def _extract_place_types(self, text):
        found = set()
        text = text.lower()
        for pt, synonyms in self.place_types.items():
            if pt in text:
                found.add(pt)
            for syn in synonyms:
                if syn in text:
                    found.add(pt)
        return list(found)

    def _extract_cuisine_types(self, text):
        found = set()
        text = text.lower()
        for ct, synonyms in self.cuisine_types.items():
            if ct in text:
                found.add(ct)
            for syn in synonyms:
                if syn in text:
                    found.add(ct)
        return list(found)

    def _extract_activities(self, text):
        found = set()
        text = text.lower()
        for act in self.activity_types:
            if act in text:
                found.add(act)
        return list(found)

    def _extract_price_range(self, text):
        match = re.search(r'(precio|tarifa|costo|rango de precios)[^\d]*(\d+[\d\s\.,$€]*)', text.lower())
        if match:
            return match.group(2)
        return None

    def _extract_address(self, text):
        match = re.search(r'(dirección|direccion|ubicado en|situada en)[^\w]*(.*)', text.lower())
        if match:
            return match.group(2).strip()
        return None

    def _extract_phones(self, text):
        return re.findall(r'(\+?\d[\d\s\-]{7,})', text)

    def _extract_emails(self, text):
        return re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

    def _create_contact(self, phones, emails):
        if not phones and not emails:
            return None
        contact_uri = EX[f"contact_{uuid4()}"]
        self.graph.add((contact_uri, RDF.type, EX.Contact))
        for phone in phones:
            self.graph.add((contact_uri, EX.hasPhone, Literal(phone)))
        for email in emails:
            self.graph.add((contact_uri, EX.hasEmail, Literal(email)))
        return contact_uri

    def add_place(self, data):
        name = data.get("name")
        if not name:
            return
        place_uri = EX[f"place_{uuid4()}"]
        self.graph.add((place_uri, RDF.type, EX.TouristPlace))
        self.graph.add((place_uri, EX.hasName, Literal(name)))
        desc = data.get("description")
        if desc:
            self.graph.add((place_uri, EX.hasDescription, Literal(desc)))
        address = data.get("address")
        if address:
            self.graph.add((place_uri, EX.hasAddress, Literal(address)))
        url = data.get("url")
        if url:
            self.graph.add((place_uri, EX.hasUrl, Literal(url)))
        province = data.get("province")
        if province:
            prov_uri = self._get_or_create(province, "Province", "province")
            self.graph.add((place_uri, EX.locatedInProvince, prov_uri))
        for pt in data.get("place_types", []):
            pt_uri = self._get_or_create(pt, "PlaceType", "place_type")
            self.graph.add((place_uri, EX.hasPlaceType, pt_uri))
        for ct in data.get("cuisine_types", []):
            ct_uri = self._get_or_create(ct, "CuisineType", "cuisine")
            self.graph.add((place_uri, EX.hasCuisineType, ct_uri))
        for act in data.get("activities", []):
            act_uri = self._get_or_create(act, "Activity", "activity")
            self.graph.add((place_uri, EX.hasActivity, act_uri))
        price = data.get("price_range")
        if price:
            pr_uri = self._get_or_create(price, "PriceRange", "price_range")
            self.graph.add((place_uri, EX.hasPriceRange, pr_uri))
        contact_uri = self._create_contact(data.get("phones", []), data.get("emails", []))
        if contact_uri:
            self.graph.add((place_uri, EX.hasContact, contact_uri))

    def parse_json_folder(self, folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".json"):
                    self._parse_file(os.path.join(root, file))

    def _parse_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Nombre
            name = data.get("titulo", "").strip()
            if not name:
                print(f"Saltando {path}: sin nombre")
                return
            # Unir todos los fragmentos y secciones en un solo texto
            secciones = data.get("secciones", [])
            all_text = name + " "
            for sec in secciones:
                if isinstance(sec, dict):
                    all_text += " ".join([str(x) for x in sec.get("fragmentos", []) if isinstance(x, str)]) + " "
            all_text += " " + str(data.get("descripcion", ""))
            # Extracción avanzada
            province = self._extract_province(all_text)
            place_types = self._extract_place_types(all_text)
            cuisine_types = self._extract_cuisine_types(all_text)
            activities = self._extract_activities(all_text)
            price_range = self._extract_price_range(all_text)
            address = self._extract_address(all_text)
            phones = self._extract_phones(all_text)
            emails = self._extract_emails(all_text)
            url = data.get("url")
            # Descripción útil
            description = None
            for sec in secciones:
                if isinstance(sec, dict) and "descripcion" in sec.get("titulo", "").lower():
                    description = " ".join([str(x) for x in sec.get("fragmentos", []) if isinstance(x, str)])
            if not description or len(description) < 30:
                description = f"{name} es un lugar turístico en {province}."
            # Agregar al grafo
            self.add_place({
                "name": name,
                "description": description,
                "province": province,
                "place_types": place_types,
                "cuisine_types": cuisine_types,
                "activities": activities,
                "price_range": price_range,
                "address": address,
                "phones": phones,
                "emails": emails,
                "url": url
            })
            print(f"Procesado: {name} ({province})")
        except Exception as e:
            print(f"Error procesando {path}: {e}")

    def save(self, filepath="data/tourism.ttl"):
        self.graph.serialize(destination=filepath, format="turtle")

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
        # Agregar nombre y tipo si está disponible
        if place_types and len(place_types) > 0:
            description_parts.append(f"{name} es un {place_types[0]} ubicado en {province}.")
        else:
            description_parts.append(f"{name} es un lugar turístico en {province}.")
        # Usar la descripción principal si existe y es útil
        if main_description and len(main_description) > 50:
            if not any(generic in main_description.lower() for generic in 
                      ["información útil", "¿cómo llegar?", "horario y festividades", 
                       "comunicaciones", "servicios bancarios", "ofertas"]):
                description_parts.append(main_description)
        # Buscar fragmentos descriptivos útiles
        for fragment in fragments:
            if (len(fragment) > 50 and 
                not any(generic in fragment.lower() for generic in 
                       ["información útil", "¿cómo llegar?", "horario", "comunicaciones", 
                        "servicios bancarios", "ofertas", "festividades"]) and
                not fragment.startswith("Zona ") and
                not fragment.startswith("Tipo de")):
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

    def save(self, filepath="data/tourism.owl"):
        self.graph.serialize(destination=filepath, format="xml")

# Clases auxiliares para el tipado en _get_or_create
class Province: pass
class CuisineType: pass
class PlaceType: pass
class PriceRange: pass
class Activity: pass 
        