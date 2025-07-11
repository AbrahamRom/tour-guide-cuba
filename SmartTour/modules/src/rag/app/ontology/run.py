from ontology_builder import OntologyBuilder

builder = OntologyBuilder()
builder.parse_json_folder(r"../../data/json")  # Cambia la ruta a tu carpeta de datos
builder.save(r"../../data/tourism.owl")        # Guarda la ontología en formato OWL