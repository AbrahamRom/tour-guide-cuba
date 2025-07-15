from ontology_builder import OntologyBuilder
import os

def main():
    try:
        builder = OntologyBuilder()
        
        # Verificar que la carpeta de JSONs existe
        json_folder = r"../../data/json"
        if not os.path.exists(json_folder):
            print(f"Error: La carpeta {json_folder} no existe")
            return
        
        # Verificar que hay archivos JSON en la carpeta
        json_files_found = False
        for root, _, files in os.walk(json_folder):
            if any(file.endswith('.json') for file in files):
                json_files_found = True
                break
        
        if not json_files_found:
            print(f"Error: No se encontraron archivos JSON en {json_folder}")
            return
        
        print("Iniciando procesamiento de archivos JSON...")
        print(f"Procesando carpeta: {json_folder}")
        builder.parse_json_folder(json_folder)
        
        # Crear directorio de salida si no existe
        output_dir = r"../../data"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = r"../../data/tourism.owl"
        builder.save(output_file)
        print(f"Ontología guardada exitosamente en {output_file}")
        
        # Mostrar estadísticas del procesamiento
        stats = builder.get_statistics()
        print("\n=== Estadísticas del procesamiento ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__ == "__main__":
    main()