from .ontology_manager import OntologyManager

class OntologyRetriever:
    def __init__(self, config):
        owl_path = config.get("ontology", {}).get("owl_path")
        self.manager = OntologyManager(owl_path)
        
    def retrieve(self, query):
        """Procesa consultas en lenguaje natural y recupera información relevante"""
        query = query.lower()
        results = []
        
        # Detección de tipo de búsqueda
        if "hotel" in query or "alojamiento" in query:
            results = self.manager.search_places("hoteles", "activity")
        elif "tour" in query or "excursión" in query:
            results = self.manager.search_places("tours", "activity")
        elif "campismo" in query or "camping" in query:
            results = self.manager.search_places("campismo", "activity")
        elif "casa" in query or "vivienda" in query:
            results = self.manager.search_places("casas", "activity")
        elif "provincia" in query or "región" in query:
            province = query.split("provincia")[-1].strip()
            results = self.manager.search_places(province, "province")
        else:
            # Búsqueda general por keywords
            results = self.manager.search_places(query)
        
        # Formatear resultados
        formatted = []
        for res in results:
            desc = f"Lugar: {res['name']}"
            if res["province"]:
                desc += f" | Provincia: {res['province']}"
            if res["activity"]:
                desc += f" | Actividad: {res['activity']}"
            formatted.append(desc)
        
        # Imprimir resultados en consola
        for item in formatted:
            print(item)
        
        return formatted