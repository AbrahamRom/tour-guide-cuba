from zimply import ZIMServer
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count
from utils import summarize_article
import json
from tqdm import tqdm

def _extract_and_filter(args):
    entry, filter_func = args
    try:
        if not entry["title"] or not entry["content"]:
            return None
        soup = BeautifulSoup(entry["content"], "html.parser")
        text = soup.get_text()

        article = {
            "title": entry["title"],
            "url": entry.get("url", ""),
            "summary": summarize_article(text),
            "content": text
        }

        return article 
    # if filter_func(article) else None
    except:
        return None

def _yield_articles(zim_path):
    server = ZIMServer(zim_path)
    for entry in server.iter_articles():
        if entry and entry.get("title"):
            content = server.get_article(entry.get("url", ""))
            if content:
                yield {
                    "title": entry["title"],
                    "content": content,
                    "url": entry.get("url", "")
                }

def process_zim_file_streamed(zim_path, filter_func, output_path):
    print("📦 Cargando artículos...")
    articles_gen = _yield_articles(zim_path)
    total_estimated = 200_000  # puedes ajustar si sabes cuántos hay
    written = 0

    with Pool(cpu_count()) as pool, open(output_path, "a", encoding="utf-8") as f:
        with tqdm(total=total_estimated, desc="🔍 Filtrando artículos", unit="art") as pbar:
            batch_size = 100
            batch = []

            for article in articles_gen:
                batch.append((article, filter_func))

                if len(batch) >= batch_size:
                    results = pool.map(_extract_and_filter, batch)
                    filtered = [r for r in results if r]

                    for i, article in enumerate(filtered):
                        if written > 0:
                            f.write(",\n")  # separador JSON válido
                        json.dump(article, f, ensure_ascii=False, indent=2)
                        written += 1

                    pbar.update(len(batch))
                    batch.clear()

            # Final batch
            if batch:
                results = pool.map(_extract_and_filter, batch)
                filtered = [r for r in results if r]

                for i, article in enumerate(filtered):
                    if written > 0:
                        f.write(",\n")
                    json.dump(article, f, ensure_ascii=False, indent=2)
                    written += 1

                pbar.update(len(batch))
