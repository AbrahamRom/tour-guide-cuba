import json
import re
import os
import concurrent.futures
import unicodedata
from libzim.reader import Archive
import html2text
import time

# Configuration
ZIM_FILE_PATH = r"C:/Users/HP/Downloads/ecured_es_all_2022-03.zim"
OUTPUT_JSON = r"C:/Users/HP/Desktop/cuba_filtered_articles.json"
WORKERS = os.cpu_count() or 4
BATCH_SIZE = 500  # Reduced batch size for better memory handling

# Define filtering keywords (Spanish)
CATEGORY_KEYWORDS = {
    "culture": [
        "cultura", "tradición", "costumbre", "música", "baile", "arte",
        "literatura", "cine", "folclor", "religión", "carnaval", "tabaco",
        "ron", "guitarra", "son", "salsa"
    ],
    "history": [
        "historia", "revolución", "independencia", "guerra", "colonia",
        "figura histórica", "personaje histórico", "héroe", "batalla",
        "fidel castro", "che guevara", "josé martí", "esclavitud",
        "revolución cubana", "crisis de los misiles", "españa", "habana vieja"
    ],
    "geography": [
        "geografía", "turismo", "playa", "montaña", "ciudad", "provincia",
        "museo", "parque", "hotel", "restaurante", "varadero", "viñales",
        "trinidad", "cayo coco", "sierra maestra", "baracoa", "cayo largo",
        "malecón", "habana", "santiago de cuba", "cienfuegos"
    ],
    "travel": [
        "viaje", "transporte", "comida", "seguridad", "visado", "pasaporte",
        "moneda", "alojamiento", "consejo", "aeropuerto", "taxi", "bus",
        "peso cubano", "casa particular", "paladar", "gastronomía", "clima",
        "vacuna", "seguro médico", "festival", "itinerario", "embajada"
    ]
}

def normalize_text(text: str) -> str:
    """Normalize text for filtering: lowercase and remove diacritics"""
    text = text.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def extract_plaintext(html: str) -> str:
    """Convert HTML content to clean plaintext"""
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.ignore_emphasis = True
    return converter.handle(html).strip()

def article_passes_filter(title: str, content: str) -> bool:
    """Check if article meets inclusion criteria"""
    norm_title = normalize_text(title)
    norm_content = normalize_text(content)
    
    # Must mention Cuba in title/content
    if "cuba" not in norm_title and "cuba" not in norm_content:
        return False
    
    # Must contain at least one category keyword
    combined = norm_title + " " + norm_content
    return any(
        re.search(r'\b' + re.escape(kw) + r'\b', combined)
        for category in CATEGORY_KEYWORDS.values()
        for kw in category
    )

def process_article(entry) -> dict:
    """Process individual article and return structured data"""
    try:
        item = entry.get_item()
        content = item.content.tobytes().decode('utf-8', errors='replace')
        
        if not article_passes_filter(entry.title, content):
            return None
            
        plain_content = extract_plaintext(content)
        url_path = entry.path.lstrip("/")
        
        return {
            "title": entry.title,
            "url": f"http://{url_path}",
            "summary": plain_content[:200] + ("..." if len(plain_content) > 200 else ""),
            "content": plain_content
        }
    except Exception as e:
        print(f"Error processing {entry.path}: {str(e)}")
        return None

def process_batch(archive_path, paths):
    """Process a batch of articles in parallel"""
    archive = Archive(archive_path)
    results = []
    
    for path in paths:
        try:
            entry = archive.get_entry_by_path(path)
            if not entry.is_article():
                continue
                
            result = process_article(entry)
            if result:
                results.append(result)
        except Exception as e:
            print(f"Error processing {path}: {str(e)}")
    
    return results

def main():
    """Main processing pipeline"""
    start_time = time.time()
    archive = Archive(ZIM_FILE_PATH)
    total_entries = archive.entry_count
    
    print(f"Processing {total_entries} entries with {WORKERS} workers...")
    
    # Collect all article paths first
    article_paths = []
    for entry in archive.iter_entries():
        if entry.is_article():
            article_paths.append(entry.path)
    
    total_articles = len(article_paths)
    print(f"Found {total_articles} articles to process")
    
    # Prepare batches of paths
    batches = [
        article_paths[i:i + BATCH_SIZE]
        for i in range(0, total_articles, BATCH_SIZE)
    ]
    
    # Process batches in parallel
    processed_count = 0
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        f.write('[')  # Start JSON array
        first_article = True
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
            futures = []
            for batch in batches:
                futures.append(executor.submit(process_batch, ZIM_FILE_PATH, batch))
            
            for future in concurrent.futures.as_completed(futures):
                batch_results = future.result()
                for article in batch_results:
                    if article is None:
                        continue
                        
                    if not first_article:
                        f.write(',')
                    json.dump(article, f, ensure_ascii=False, indent=2)
                    first_article = False
                    processed_count += 1
                    
                    # Progress tracking
                    if processed_count % 100 == 0:
                        elapsed = time.time() - start_time
                        print(f"Processed: {processed_count}/{total_articles} | "
                              f"Speed: {processed_count/elapsed:.2f} articles/sec")
        
        f.write(']')  # Close JSON array
    
    elapsed = time.time() - start_time
    print(f"Completed! {processed_count} articles saved to {OUTPUT_JSON}")
    print(f"Total processing time: {elapsed:.2f} seconds")
    print(f"Processing speed: {processed_count/elapsed:.2f} articles/sec")

if __name__ == "__main__":
    main()