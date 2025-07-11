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
    value = re.sub(r'[^\w\s-]', '', value)  # Solo letras, números, guion y espacio
    value = value.replace(" ", "_").replace("__", "_")
    value = value.strip("_").lower()
    # Si después de limpiar queda vacío, retorna None
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
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            secciones = data.get("secciones", [])
            fragments = sum((sec.get("fragmentos", []) for sec in secciones), [])

            provincia = None
            cocina = []
            precio = None
            descripcion = ""
            nombre = data.get("titulo") or os.path.basename(path)
            place_types = []
            address = None
            url = data.get("url")
            phones = data.get("telefonos", [])
            emails = data.get("emails", [])
            activities = []

            # Provincia
            for frag in fragments:
                if frag.startswith("Zona "):
                    provincia = frag.replace("Zona ", "").strip()
                    break
                if frag.startswith("Sobre "):
                    provincia = frag.replace("Sobre ", "").strip()
                    break
                if frag.startswith("Destinos "):
                    # Tomar el primer destino como provincia principal
                    provincia = frag.replace("Destinos ", "").split()[0]
                    break

            # Tipos de cocina
            for frag in fragments:
                if "Tipo de Cocina" in frag:
                    cocina = [c.strip() for c in frag.replace("Tipo de Cocina", "").replace("Cocina", "").split() if len(c.strip()) > 2 and c.lower() not in ["de", "tipo"]]
                    break

            # Rango de precios
            for frag in fragments:
                if "Rango de precios" in frag:
                    precio = frag.replace("Rango de precios", "").strip()
                    break

            # Tipos de lugar
            for frag in fragments:
                if "Tipo de lugar" in frag:
                    place_types = [t.strip() for t in frag.replace("Tipo de lugar", "").split() if len(t.strip()) > 2]
                    break

            # Dirección
            for frag in fragments:
                if "Dirección:" in frag:
                    address = frag.split("Dirección:")[-1].strip()
                    break

            # Actividades, paquetes, eventos (heurística simple)
            for frag in fragments:
                if any(word in frag.lower() for word in ["evento", "paquete", "excursión", "actividad", "golf", "vacaciones", "combinados", "premium", "plan viaje"]):
                    acts = [a.strip() for a in frag.split() if len(a.strip()) > 3]
                    activities.extend(acts)

            # Descripción (primer fragmento largo que no sea cocina, provincia, precio, tipo de lugar)
            for frag in fragments:
                if (
                    frag not in (provincia or "")
                    and frag not in " ".join(cocina)
                    and frag not in " ".join(place_types)
                    and (not precio or frag != precio)
                    and len(frag) > 30
                    and not frag.startswith("Tipo de Cocina")
                    and not frag.startswith("Rango de precios")
                    and not frag.startswith("Zona ")
                    and not frag.startswith("Sobre ")
                    and not frag.startswith("Tipo de lugar")
                ):
                    descripcion = frag
                    break

            # Si no se encontró provincia, buscar en fragmentos que contengan "Provincia:"
            if not provincia:
                for frag in fragments:
                    if "Provincia:" in frag:
                        provincia = frag.split("Provincia:")[-1].strip()
                        break

            # Si no se encontró cocina, buscar fragmentos con palabras típicas de cocina
            if not cocina:
                for frag in fragments:
                    if any(word in frag.lower() for word in ["cocina", "asados", "cubana", "italiana", "internacional", "gourmet", "vegana", "vegetariana"]):
                        cocina = [c.strip() for c in frag.split() if len(c.strip()) > 2]
                        break

            # Si no se encontró descripción, usar el primer fragmento largo
            if not descripcion:
                for frag in fragments:
                    if len(frag) > 30:
                        descripcion = frag
                        break

            provincia = provincia or "Unknown"
            nombre = nombre or os.path.basename(path)

            self.add_place(
                nombre, provincia, cocina, descripcion, precio,
                place_types=place_types, address=address, url=url,
                phones=phones, emails=emails, activities=activities
            )

    def save(self, filepath="data/tourism.owl"):
        self.graph.serialize(destination=filepath, format="xml")

# Clases auxiliares para el tipado en _get_or_create
class Province: pass
class CuisineType: pass
class PlaceType: pass
class PriceRange: pass
class Activity: pass
