import wikipedia
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from fake_useragent import UserAgent

def clean_text(text):
    # Elimina corchetes de referencias [1], [2], etc.
    text = re.sub(r"\[\d+\]", "", text)
    # Elimina múltiples espacios
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_main_content(url, headers=None):
    try:
        response = requests.get(url, headers=headers or {}, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        # Busca el contenido principal en los párrafos
        paragraphs = soup.find_all("p")
        # Extrae los primeros 2-3 párrafos útiles
        text = "\n".join(p.get_text(strip=True) for p in paragraphs[:3])
        return text.strip() if text else None

    except Exception as e:
        print(f"[ContentExtractor] ❌ Error al procesar {url}: {e}")
        return None

def search_wikipedia(query, lang="es"):
    """
    Busca la entrada más relevante en Wikipedia y extrae su introducción.
    Si hay ambigüedad o desambiguación, elige el primer resultado posible.
    """
    try:
        wikipedia.set_lang(lang)
        results = wikipedia.search(query)
 
        if not results:
            return None

        for title in results:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                # Usamos solo la parte introductoria del contenido
                summary = page.summary
                return clean_text(summary)
            except wikipedia.exceptions.DisambiguationError as e:
                # Elegimos la primera opción sugerida de la página de desambiguación
                try:
                    sub_page = wikipedia.page(e.options[0], auto_suggest=False)
                    return clean_text(sub_page.summary)
                except:
                    continue
            except Exception:
                continue

    except Exception as e:
        print(f"[WikipediaScraper] ❌ Error al buscar en Wikipedia: {e}")

    return None

def search_duckduckgo_top3(query, lang="es"):
    """
    Busca la query en DuckDuckGo y devuelve el contenido principal de los 3 primeros resultados.
    """
    headers = {
        "User-Agent": UserAgent().random
    }

    search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
    try:
        resp = requests.get(search_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"[DuckDuckGo] ❌ Error en búsqueda: {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results = soup.select(".result__a")

        if not results:
            print("[DuckDuckGo] ⚠️ No se encontraron resultados.")
            return []

        top_links = []
        for link in results[:3]:
            href = link.get("href")
            if not href.startswith("http"):
                href = "https:" + href
            top_links.append(href)

        # Extrae el contenido principal de cada enlace
        contents = []
        for url in top_links:
            content = extract_main_content(url, headers)
            if content:
                contents.append(content)
        return contents

    except Exception as e:
        print(f"[DuckDuckGo] ❌ Error general: {e}")
        return []

def search_dynamic(query, lang="es"):
    """
    Devuelve una lista con el resultado más importante de Wikipedia y los 3 más importantes de DuckDuckGo.
    """
    results = []
    # Wikipedia (solo el más relevante)
    wiki_result = search_wikipedia(query, lang)
    if wiki_result:
        results.append({"source": "wikipedia", "content": wiki_result})

    # DuckDuckGo (top 3)
    duck_results = search_duckduckgo_top3(query, lang)
    for idx, content in enumerate(duck_results):
        results.append({"source": f"duckduckgo_{idx+1}", "content": content})

    return results
