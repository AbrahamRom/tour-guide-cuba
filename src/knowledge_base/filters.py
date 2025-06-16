import re

KEYWORDS = [
    "Cuba", "cubano", "cubana", "La Habana", "Santiago de Cuba",
    "cultura cubana", "turismo en Cuba", "revolución cubana",
    "música cubana", "comida cubana", "lugares turísticos en Cuba"
]

CATEGORIES = [
    "historia", "turismo", "geografía", "cultura", "costumbres", "viaje",
    "transporte", "seguridad", "gastronomía", "tradiciones", "fiestas"
]

def cuban_article_filter(article):
    if not article.get("title") or not article.get("content"):
        return False

    title = article["title"].lower()
    body = article["content"].lower()

    # Rule 1: "Cuba" or related in title or body
    if any(k.lower() in title or k.lower() in body for k in KEYWORDS):
        return True

    # Rule 2: Category relevance
    if any(cat in body for cat in CATEGORIES):
        return True

    return False
