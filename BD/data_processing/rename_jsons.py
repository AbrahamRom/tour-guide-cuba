import os
import json
import re
import shutil

input_dir = "../datas/raw"
output_dir = "../datas/renamed"

os.makedirs(output_dir, exist_ok=True)

def slugify(text):
    # Convierte texto a minúsculas, reemplaza espacios y elimina caracteres no válidos
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")

for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith(".json"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Extrae nombre del restaurante y ciudad desde la URL si es posible
                url = data.get("url", "")
                match = re.search(r"/es/([^/]+)/restaurant/([^/#]+)", url)
                if match:
                    ciudad = match.group(1)
                    nombre = match.group(2)
                else:
                    ciudad = "desconocido"
                    nombre = data.get("titulo", "sin_nombre")
                nombre_archivo = f"{slugify(ciudad)}_{slugify(nombre)}.json"
                output_path = os.path.join(output_dir, nombre_archivo)
                shutil.copy(file_path, output_path)
            except Exception as e:
                print(f"Error procesando {file_path}: {e}")

print("Renombrado finalizado. Archivos guardados en:", output_dir)