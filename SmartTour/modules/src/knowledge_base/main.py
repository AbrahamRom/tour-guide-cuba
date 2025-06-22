from processor import extract_articles
from filters import cuban_article_filter
from config import ZIM_PATH

if __name__ == "__main__":
    print("🚀 Iniciando extracción desde:", ZIM_PATH)
    extract_articles(ZIM_PATH, cuban_article_filter)
    print("✅ ¡Proceso finalizado con éxito!")