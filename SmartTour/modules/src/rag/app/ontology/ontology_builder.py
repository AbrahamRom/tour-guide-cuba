from rdflib import Graph, Literal, RDF, RDFS, Namespace, URIRef
from rdflib.namespace import OWL, XSD
import os, json
from uuid import uuid4
import unicodedata
import re

EX = Namespace("http://smarttour.org/tourism#")

def clean_uri(value):
    # Elimina tildes, convierte a ascii, elimina comillas, paréntesis, puntos, comas, etc.
    value = str(value or "")
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value)
    value = value.replace(" ", "_").replace("__", "_")
    value = value.strip("_").lower()
    return value if value else None

class OntologyBuilder:
    def __init__(self):
        self.graph = Graph()
        self.graph.bind("ex", EX)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
        self.provinces = set()
        self.cuisine_types = set()
        self.place_types = set()
        self.price_ranges = set()
        self.activities = set()
        self.contacts = set()
        self._define_schema()

    def _define_schema(self):
        # Clases
        self.graph.add((EX.TouristPlace, RDF.type, OWL.Class))
        self.graph.add((EX.Province, RDF.type, OWL.Class))
        self.graph.add((EX.CuisineType, RDF.type, OWL.Class))
        self.graph.add((EX.PlaceType, RDF.type, OWL.Class))
        self.graph.add((EX.PriceRange, RDF.type, OWL.Class))
        self.graph.add((EX.Contact, RDF.type, OWL.Class))
        self.graph.add((EX.Activity, RDF.type, OWL.Class))
        # Object properties
        self.graph.add((EX.locatedInProvince, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasCuisineType, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasPlaceType, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasPriceRange, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasContact, RDF.type, OWL.ObjectProperty))
        self.graph.add((EX.hasActivity, RDF.type, OWL.ObjectProperty))
        # Data properties
        self.graph.add((EX.hasName, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasDescription, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasAddress, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasPhone, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasEmail, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.hasUrl, RDF.type, OWL.DatatypeProperty))
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

    def _get_or_create(self, name, cls, cache_set):
        safe_name = clean_uri(name)
        if not safe_name:
            # No crear recursos para valores vacíos o nulos
            return None
        uri = EX[f"{cls.__name__.lower()}_{safe_name}"]
        if name not in cache_set:
            self.graph.add((uri, RDF.type, getattr(EX, cls.__name__)))
            self.graph.add((uri, RDFS.label, Literal(name)))
            cache_set.add(name)
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

    def add_place(self, name, province, cuisine_types, description, price_range=None, place_types=None, address=None, url=None, phones=None, emails=None, activities=None):
        place_uri = EX[str(uuid4())]
        self.graph.add((place_uri, RDF.type, EX.TouristPlace))
        self.graph.add((place_uri, EX.hasName, Literal(name)))
        self.graph.add((place_uri, EX.hasDescription, Literal(description)))
        if address:
            self.graph.add((place_uri, EX.hasAddress, Literal(address)))
        if url:
            self.graph.add((place_uri, EX.hasUrl, Literal(url)))
        if province:
            prov_uri = self._get_or_create_province(province)
            if prov_uri:
                self.graph.add((place_uri, EX.locatedInProvince, prov_uri))
        # Filtrar valores vacíos o nulos antes de crear recursos
        for cuisine in filter(None, cuisine_types or []):
            cuisine_uri = self._get_or_create_cuisine(cuisine)
            if cuisine_uri:
                self.graph.add((place_uri, EX.hasCuisineType, cuisine_uri))
        for pt in filter(None, place_types or []):
            pt_uri = self._get_or_create_place_type(pt)
            if pt_uri:
                self.graph.add((place_uri, EX.hasPlaceType, pt_uri))
        if price_range:
            pr_uri = self._get_or_create_price_range(price_range)
            if pr_uri:
                self.graph.add((place_uri, EX.hasPriceRange, pr_uri))
        if (phones or emails):
            contact_uri = self._create_contact(phones or [], emails or [])
            self.graph.add((place_uri, EX.hasContact, contact_uri))
        for act in filter(None, activities or []):
            act_uri = self._get_or_create_activity(act)
            if act_uri:
                self.graph.add((place_uri, EX.hasActivity, act_uri))

    def parse_json_folder(self, folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".json"):
                    self._parse_file(os.path.join(root, file))

    def _parse_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Verificar que data no sea None y sea un diccionario
                if not isinstance(data, dict):
                    print(f"Archivo {path} no contiene un diccionario válido, saltando...")
                    return

                secciones = data.get("secciones", [])
                if not isinstance(secciones, list):
                    secciones = []

                all_fragments = []
                structured_content = {}

                # --------- CORREGIDO: OBTENER EL NOMBRE DEL LUGAR SOLO DEL CAMPO 'titulo' ---------
                nombre = ""
                if "titulo" in data and isinstance(data["titulo"], str):
                    nombre = data["titulo"].strip()
                # Si no hay nombre, no procesar el lugar
                if not nombre:
                    print(f"Archivo {path} no tiene campo 'titulo' válido, saltando...")
                    return
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
                    print(f"Archivo {path} no contiene información suficiente, saltando...")
                    return
                
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
                    self.add_place(
                        nombre, provincia, cocina, descripcion, precio,
                        place_types=place_types if place_types else None, address=address, url=url,
                        phones=phones, emails=emails, activities=activities
                    )
                else:
                    print(f"Lugar '{nombre}' no tiene información suficiente para ser agregado")
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON en {path}: {e}")
        except Exception as e:
            print(f"Error procesando archivo {path}: {e}")

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
        