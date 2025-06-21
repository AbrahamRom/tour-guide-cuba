import re

def get_snippet(text, query, window=40):
    pattern = re.escape(query)
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        start, end = match.start(), match.end()
        return f"...{text[max(0, start-window):min(len(text), end+window)]}..."
    return text[:200] + "..."
