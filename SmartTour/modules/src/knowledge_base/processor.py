import json
from bs4 import BeautifulSoup
from zimply import ZIMServer
from config import OUTPUT_PATH, BATCH_SIZE, MIN_TEXT_LENGTH
from utils import summarize_article, clean_text
from tqdm import tqdm

def extract_articles(zim_path, filter_func):
    server = ZIMServer(zim_path)
    articles = list(server.iter_articles())
    total = len(articles)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("[\n")

        first = True
        for i, entry in enumerate(tqdm(articles, desc="⏳ Procesando artículos", unit="art")):
            try:
                if not entry or not entry.get("url") or not entry.get("title"):
                    continue

                raw_content = server.get_article(entry["url"])
                if not raw_content:
                    continue

                soup = BeautifulSoup(raw_content, "html.parser")
                text = clean_text(soup.get_text())

                if len(text) < MIN_TEXT_LENGTH:
                    continue

                article = {
                    "title": entry["title"],
                    "url": entry.get("url", ""),
                    "summary": summarize_article(text),
                    "content": text
                }

                if filter_func(article):
                    if not first:
                        f.write(",\n")
                    json.dump(article, f, ensure_ascii=False, indent=2)
                    first = False

            except Exception as e:
                print(f"❌ Error en artículo {i}: {e}")

        f.write("\n]\n")
