from ontology_builder import OntologyBuilder
import os

def main():
    try:
        builder = OntologyBuilder()
        
        # Verificar que la carpeta de datos existe
        data_folder = r"../../data/json/www_cuba_travel"
        if not os.path.exists(data_folder):
            print(f"Error: La carpeta {data_folder} no existe")
            return
        
        print("Procesando archivos JSON...")
        builder.parse_json_folder(data_folder)
        
        # Crear directorio de salida si no existe
        output_dir = r"../../data"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = r"../../data/tourism.ttl"
        builder.save(output_file)
        print(f"Ontología guardada exitosamente en {output_file} (formato Turtle)")
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__ == "__main__":
    main()