import os
import json
from zimply import ZIMArchive
from tqdm import tqdm

ZIM_PATH = "C:/Users/HP/Downloads/ecured_es_all_2022-03.zim"
OUTPUT_PATH = "C:/Users/HP/Desktop/cuba_filtered_articles.json"

def is_cuba_related(title: str, content: str) -> bool:
    title = title.lower()
    content = content.lower()
    keywords = ["cuba", "cubano", "cubana", "havana", "la habana", "santiago de cuba", "revolución cubana"]
    return any(k in title or k in content for k in keywords)

def main():
    print(f"Opening ZIM file: {ZIM_PATH}")
    zim = ZIMArchive(ZIM_PATH)

    total_entries = len(zim.entries)
    print(f"Total entries found: {total_entries}")

    filtered = []
    for entry in tqdm(zim.entries, desc="Processing articles"):
        if not entry.namespace == 'A':  # skip non-article entries
            continue
        try:
            content = zim.read_article(entry)
            if content and is_cuba_related(entry.title, content):
                filtered.append({
                    "title": entry.title,
                    "url": entry.url,
                    "namespace": entry.namespace,
                    "content": content[:3000]  # limit to 3000 characters to avoid overload
                })
        except Exception as e:
            print(f"Failed to read article: {entry.title} – {e}")

    print(f"\nTotal Cuba-related articles found: {len(filtered)}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
