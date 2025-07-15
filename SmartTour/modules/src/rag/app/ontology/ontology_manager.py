import rdflib
from rdflib import URIRef, RDF
import os
import json
from datetime import datetime

class OntologyManager:
    def __init__(self, owl_path="modules/src/rag/data/tourism.ttl"):
        self.graph = rdflib.Graph()
        self.graph.parse(owl_path, format="ttl")
        self.ns = {"ex": "http://smarttour.org/tourism#"}
        self.ex = rdflib.Namespace(self.ns["ex"])
        
    def get_all_places(self):
        """Obtiene todos los lugares turísticos con sus propiedades"""
        query = """
        PREFIX ex: <http://smarttour.org/tourism#>
        SELECT ?place ?name ?province ?activity
        WHERE {
            ?place a ex:LugarTuristico .
            ?place ex:tieneNombre ?name .
            OPTIONAL { ?place ex:estaEnProvincia ?province } .
            OPTIONAL { ?place ex:ofreceActividad ?activity } .
        }
        """
        return self.graph.query(query)

    def search_places(self, search_term, search_type="keyword"):
        """
        Busca lugares turísticos por:
        - keyword: búsqueda en todos los campos
        - name: solo en nombres
        - province: solo en provincias
        - activity: solo en actividades
        """
        search_term = search_term.lower()
        results = []
        
        for row in self.get_all_places():
            place_data = {
                "name": str(row.name),
                "province": str(row.province.split("/")[-1]) if row.province else None,
                "activity": str(row.activity)
            }
            
            if search_type == "keyword":
                if (search_term in place_data["name"].lower() or 
                    (place_data["province"] and search_term in place_data["province"].lower()) or 
                    (place_data["activity"] and search_term in place_data["activity"].lower())):
                    results.append(place_data)
                    
            elif search_type == "name" and search_term in place_data["name"].lower():
                results.append(place_data)
                
            elif search_type == "province" and place_data["province"] and search_term in place_data["province"].lower():
                results.append(place_data)
                
            elif search_type == "activity" and place_data["activity"] and search_term in place_data["activity"].lower():
                results.append(place_data)
                
        return results
    
    def insert_fallback_knowledge(self, query, context):
        """
        Inserta conocimiento de fallback en formato JSON estructurado
        dentro de la carpeta data/json para futuras consultas.
        """
        data_dir = "modules/src/rag/data/json/fallback_knowledge"
        os.makedirs(data_dir, exist_ok=True)
        now = datetime.now().isoformat()
        # Sanitiza la query para usarla como nombre de archivo
        safe_query = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in query)
        safe_query = safe_query.replace(" ", "_")
        filename = os.path.join(data_dir, f"fallback_knowledge_{safe_query}.json")
        knowledge = {
            "query": query,
            "context": context,
            "date": now
        }
        # Si el archivo existe, carga y agrega; si no, crea nuevo
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, list):
                existing.append(knowledge)
            else:
                existing = [existing, knowledge]
        else:
            existing = [knowledge]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)