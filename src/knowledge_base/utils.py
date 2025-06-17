import re

def summarize_article(text, max_sentences=3):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:max_sentences]) if sentences else ""

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()