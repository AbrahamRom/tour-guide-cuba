from processor import process_zim_file_streamed
from filters import cuban_article_filter
import os

ZIM_FILE = r"C:\Users\HP\Downloads\ecured_es_all_2022-03.zim"
OUTPUT_FILE = "cuban_articles.json"

if __name__ == "__main__":
    print("🚀 Procesando archivo .zim en tiempo real...")

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("[\n")  # inicio del array

    process_zim_file_streamed(ZIM_FILE, cuban_article_filter, OUTPUT_FILE)

    # Cierra el JSON correctamente
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write("\n]")
    
    print(f"\n✅ JSON guardado dinámicamente en {OUTPUT_FILE}")
