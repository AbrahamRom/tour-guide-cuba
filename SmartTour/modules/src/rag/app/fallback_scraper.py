import wikipedia
import re
from bs4 import BeautifulSoup

def clean_text(text):
    # Elimina corchetes de referencias [1], [2], etc.
    text = re.sub(r"\[\d+\]", "", text)
    # Elimina múltiples espacios
    text = re.sub(r"\s+", " ", text)
    return text.strip()

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
