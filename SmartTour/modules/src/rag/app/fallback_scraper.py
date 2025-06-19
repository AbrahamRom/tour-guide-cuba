import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def search_ecured(query):
    search_url = f"https://www.ecured.cu/index.php?title=Especial:Buscar&search={quote(query)}"
    resp = requests.get(search_url, timeout=10)

    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    # Encuentra el primer enlace de artículo
    result = soup.select_one(".mw-search-result-heading a")
    if not result:
        return None

    article_url = "https://www.ecured.cu" + result["href"]
    return extract_article_text(article_url)

def extract_article_text(url):
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    content_div = soup.find("div", {"class": "mw-parser-output"})
    if not content_div:
        return None

    paragraphs = content_div.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs[:3])  # solo primeros párrafos
    return text.strip() if text else None
