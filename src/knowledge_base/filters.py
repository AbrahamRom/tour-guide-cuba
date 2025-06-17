KEYWORDS = [
    "Cuba", "cubano", "cubana", "La Habana", "Santiago de Cuba",
    "Varadero", "revolución cubana", "José Martí", "Che Guevara",
    "comida cubana", "turismo en Cuba", "música cubana", "Ron", "tabaco"
]

def cuban_article_filter(article):
    text = (article["title"] + " " + article["content"]).lower()
    return any(word.lower() in text for word in KEYWORDS)
