import os
import json
import re

raw_dir = '../datas/raw'

def slugify(text):
    text = text.lower()
    text = re.sub(r'https?://', '', text)
    text = re.sub(r'www\.', '', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text[:80]

for fname in os.listdir(raw_dir):
    if fname.endswith('.json'):
        fpath = os.path.join(raw_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                continue
        url = data.get('url', '')
        titulo = data.get('titulo', '')
        # Usa parte de la URL o el título para el nombre
        if '/restaurant/' in url:
            parts = url.split('/')
            provincia = parts[4] if len(parts) > 4 else 'desconocido'
            nombre = parts[6] if len(parts) > 6 else 'sin-nombre'
            new_name = f"{provincia}_{nombre}.json"
        elif titulo:
            new_name = slugify(titulo) + '.json'
        else:
            new_name = slugify(url) + '.json'
        new_path = os.path.join(raw_dir, new_name)
        # Evita sobrescribir archivos existentes
        if not os.path.exists(new_path):
            os.rename(fpath, new_path)