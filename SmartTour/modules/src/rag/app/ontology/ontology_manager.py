from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery
import uuid

EX = Namespace("http://smarttour.org/tourism#")  # Cambiado el namespace

class OntologyManager:
    def __init__(self, owl_path="data/tourism.owl"):
        self.graph = Graph()
        self.graph.parse(owl_path, format="xml")

    def search_places_by_province(self, province_name):
        q = prepareQuery("""
        SELECT ?name ?desc WHERE {
            ?place a ex:TouristPlace ;
                   ex:hasName ?name ;
                   ex:hasDescription ?desc ;
                   ex:locatedInProvince ?prov .
            FILTER(CONTAINS(LCASE(?prov), LCASE(?province)))
        }
        """, initNs={"ex": EX})

        return self.graph.query(q, initBindings={"province": Literal(province_name)})

    def insert_fallback_knowledge(self, name, province, description):
        """
        Inserta una nueva instancia de TouristPlace en la ontología usando información de fallback.
        - name: nombre del lugar (string)
        - province: nombre de la provincia (string)
        - description: puede ser string o lista de dicts con 'content'
        """
        # Procesar el campo description/context
        desc_text = ""
        if isinstance(description, list):
            # Lista de dicts: extraer y concatenar los contenidos
            desc_text = "\n".join(
                d.get("content", "") for d in description if isinstance(d, dict) and d.get("content")
            )
        elif isinstance(description, str):
            desc_text = description
        else:
            desc_text = str(description)

        # Crear un URI único para el nuevo lugar
        place_uri = EX["FallbackPlace_" + str(uuid.uuid4())]

        # Añadir triples a la ontología
        self.graph.add((place_uri, EX.hasName, Literal(name)))
        self.graph.add((place_uri, EX.hasDescription, Literal(desc_text)))
        self.graph.add((place_uri, EX.locatedInProvince, Literal(province)))
        self.graph.add((place_uri, EX.type, EX.TouristPlace))

        # Opcional: guardar los cambios en el archivo OWL
        # self.graph.serialize(destination="data/tourism.owl", format="xml")
