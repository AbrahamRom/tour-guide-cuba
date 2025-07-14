from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
import uuid

EX = Namespace("http://smarttour.org/tourism#")

class OntologyManager:
    def __init__(self, owl_path="data/tourism.owl"):
        self.graph = Graph()
        self.graph.bind("ex", EX)
        try:
            self.graph.parse(owl_path, format="xml")
            print(f"Ontología cargada exitosamente desde {owl_path}")
            print(f"Número de triples: {len(self.graph)}")
        except Exception as e:
            print(f"Error cargando ontología: {e}")

    def search_places_by_province(self, province_name):
        """Busca lugares por provincia con información más detallada"""
        q = prepareQuery("""
        SELECT ?place ?name ?desc ?address ?province WHERE {
            ?place a ex:TouristPlace ;
                   ex:hasName ?name ;
                   ex:hasDescription ?desc ;
                   ex:locatedInProvince ?prov .
            ?prov rdfs:label ?province .
            OPTIONAL { ?place ex:hasAddress ?address }
            FILTER(CONTAINS(LCASE(?province), LCASE(?provinceName)))
        }
        ORDER BY ?name
        """, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        
        results = self.graph.query(q, initBindings={'provinceName': province_name})
        
        places = []
        for row in results:
            place_info = {
                'uri': str(row.place),
                'name': str(row.name),
                'desc': str(row.desc),
                'province': str(row.province),
                'address': str(row.address) if row.address else None
            }
            places.append(place_info)
        
        return places

    def search_places_by_type(self, place_type):
        """Busca lugares por tipo"""
        q = prepareQuery("""
        SELECT ?place ?name ?desc ?province ?placeType WHERE {
            ?place a ex:TouristPlace ;
                   ex:hasName ?name ;
                   ex:hasDescription ?desc ;
                   ex:hasPlaceType ?typeUri ;
                   ex:locatedInProvince ?provUri .
            ?typeUri rdfs:label ?placeType .
            ?provUri rdfs:label ?province .
            FILTER(CONTAINS(LCASE(?placeType), LCASE(?searchType)))
        }
        ORDER BY ?name
        """, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        
        results = self.graph.query(q, initBindings={'searchType': place_type})
        
        places = []
        for row in results:
            place_info = {
                'uri': str(row.place),
                'name': str(row.name),
                'desc': str(row.desc),
                'province': str(row.province),
                'type': str(row.placeType)
            }
            places.append(place_info)
        
        return places

    def search_places_by_cuisine(self, cuisine_type):
        """Busca lugares por tipo de cocina"""
        q = prepareQuery("""
        SELECT ?place ?name ?desc ?province ?cuisine WHERE {
            ?place a ex:TouristPlace ;
                   ex:hasName ?name ;
                   ex:hasDescription ?desc ;
                   ex:hasCuisineType ?cuisineUri ;
                   ex:locatedInProvince ?provUri .
            ?cuisineUri rdfs:label ?cuisine .
            ?provUri rdfs:label ?province .
            FILTER(CONTAINS(LCASE(?cuisine), LCASE(?searchCuisine)))
        }
        ORDER BY ?name
        """, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        
        results = self.graph.query(q, initBindings={'searchCuisine': cuisine_type})
        
        places = []
        for row in results:
            place_info = {
                'uri': str(row.place),
                'name': str(row.name),
                'desc': str(row.desc),
                'province': str(row.province),
                'cuisine': str(row.cuisine)
            }
            places.append(place_info)
        
        return places

    def search_places_by_activity(self, activity):
        """Busca lugares por actividad"""
        q = prepareQuery("""
        SELECT ?place ?name ?desc ?province ?activity WHERE {
            ?place a ex:TouristPlace ;
                   ex:hasName ?name ;
                   ex:hasDescription ?desc ;
                   ex:hasActivity ?actUri ;
                   ex:locatedInProvince ?provUri .
            ?actUri rdfs:label ?activity .
            ?provUri rdfs:label ?province .
            FILTER(CONTAINS(LCASE(?activity), LCASE(?searchActivity)))
        }
        ORDER BY ?name
        """, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        
        results = self.graph.query(q, initBindings={'searchActivity': activity})
        
        places = []
        for row in results:
            place_info = {
                'uri': str(row.place),
                'name': str(row.name),
                'desc': str(row.desc),
                'province': str(row.province),
                'activity': str(row.activity)
            }
            places.append(place_info)
        
        return places

    def search_by_keywords(self, keywords):
        """Busca lugares usando palabras clave en nombre y descripción"""
        keyword_filter = " || ".join([f"CONTAINS(LCASE(?searchText), LCASE('{kw}'))" for kw in keywords])
        
        query_str = f"""
        SELECT ?place ?name ?desc ?province WHERE {{
            ?place a ex:TouristPlace ;
                   ex:hasName ?name ;
                   ex:hasDescription ?desc ;
                   ex:locatedInProvince ?provUri .
            ?provUri rdfs:label ?province .
            BIND(CONCAT(LCASE(?name), " ", LCASE(?desc)) AS ?searchText)
            FILTER({keyword_filter})
        }}
        ORDER BY ?name
        """
        
        q = prepareQuery(query_str, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        results = self.graph.query(q)
        
        places = []
        for row in results:
            place_info = {
                'uri': str(row.place),
                'name': str(row.name),
                'desc': str(row.desc),
                'province': str(row.province)
            }
            places.append(place_info)
        
        return places

    def get_all_places(self):
        """Obtiene todos los lugares turísticos"""
        q = prepareQuery("""
        SELECT ?place ?name ?desc ?province WHERE {
            ?place a ex:TouristPlace ;
                   ex:hasName ?name ;
                   ex:hasDescription ?desc ;
                   ex:locatedInProvince ?provUri .
            ?provUri rdfs:label ?province .
        }
        ORDER BY ?name
        """, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        
        results = self.graph.query(q)
        
        places = []
        for row in results:
            place_info = {
                'uri': str(row.place),
                'name': str(row.name),
                'desc': str(row.desc),
                'province': str(row.province)
            }
            places.append(place_info)
        
        return places

    def get_provinces(self):
        """Obtiene todas las provincias disponibles"""
        q = prepareQuery("""
        SELECT DISTINCT ?province WHERE {
            ?prov a ex:Province ;
                  rdfs:label ?province .
        }
        ORDER BY ?province
        """, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        
        results = self.graph.query(q)
        return [str(row.province) for row in results]

    def get_place_types(self):
        """Obtiene todos los tipos de lugar disponibles"""
        q = prepareQuery("""
        SELECT DISTINCT ?type WHERE {
            ?typeUri a ex:PlaceType ;
                     rdfs:label ?type .
        }
        ORDER BY ?type
        """, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        
        results = self.graph.query(q)
        return [str(row.type) for row in results]

    def get_cuisine_types(self):
        """Obtiene todos los tipos de cocina disponibles"""
        q = prepareQuery("""
        SELECT DISTINCT ?cuisine WHERE {
            ?cuisineUri a ex:CuisineType ;
                        rdfs:label ?cuisine .
        }
        ORDER BY ?cuisine
        """, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        
        results = self.graph.query(q)
        return [str(row.cuisine) for row in results]

    def get_place_details(self, place_uri):
        """Obtiene detalles completos de un lugar específico"""
        q = prepareQuery("""
        SELECT ?name ?desc ?province ?address ?url 
               (GROUP_CONCAT(DISTINCT ?cuisine; separator=", ") AS ?cuisines)
               (GROUP_CONCAT(DISTINCT ?placeType; separator=", ") AS ?types)
               (GROUP_CONCAT(DISTINCT ?activity; separator=", ") AS ?activities)
               (GROUP_CONCAT(DISTINCT ?phone; separator=", ") AS ?phones)
               (GROUP_CONCAT(DISTINCT ?email; separator=", ") AS ?emails)
        WHERE {
            ?place ex:hasName ?name ;
                   ex:hasDescription ?desc ;
                   ex:locatedInProvince ?provUri .
            ?provUri rdfs:label ?province .
            
            OPTIONAL { ?place ex:hasAddress ?address }
            OPTIONAL { ?place ex:hasUrl ?url }
            OPTIONAL { 
                ?place ex:hasCuisineType ?cuisineUri .
                ?cuisineUri rdfs:label ?cuisine 
            }
            OPTIONAL { 
                ?place ex:hasPlaceType ?typeUri .
                ?typeUri rdfs:label ?placeType 
            }
            OPTIONAL { 
                ?place ex:hasActivity ?actUri .
                ?actUri rdfs:label ?activity 
            }
            OPTIONAL { 
                ?place ex:hasContact ?contact .
                ?contact ex:hasPhone ?phone 
            }
            OPTIONAL { 
                ?place ex:hasContact ?contact .
                ?contact ex:hasEmail ?email 
            }
            
            FILTER(?place = ?placeUri)
        }
        GROUP BY ?name ?desc ?province ?address ?url
        """, initNs={"ex": EX, "rdfs": "http://www.w3.org/2000/01/rdf-schema#"})
        
        results = self.graph.query(q, initBindings={'placeUri': place_uri})
        
        for row in results:
            return {
                'name': str(row.name),
                'desc': str(row.desc),
                'province': str(row.province),
                'address': str(row.address) if row.address else None,
                'url': str(row.url) if row.url else None,
                'cuisines': str(row.cuisines).split(", ") if row.cuisines else [],
                'types': str(row.types).split(", ") if row.types else [],
                'activities': str(row.activities).split(", ") if row.activities else [],
                'phones': str(row.phones).split(", ") if row.phones else [],
                'emails': str(row.emails).split(", ") if row.emails else []
            }
        
        return None
