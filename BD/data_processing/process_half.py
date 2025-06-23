import json
import random

input_path = 'processed/normalized_data.json'
output_path = 'processed/normalized_data_half.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Si es un diccionario con una lista, ajusta según la estructura real
if isinstance(data, list):
    items = data
else:
    # Si el JSON es un dict con una clave principal tipo "data" o similar
    # items = data['data']
    raise Exception("El JSON no es una lista. Ajusta el script según la estructura.")

half = len(items) // 2
selected = random.sample(items, half)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)