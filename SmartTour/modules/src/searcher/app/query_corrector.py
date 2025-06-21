from difflib import get_close_matches

def suggest_query(user_query, corpus_titles, cutoff=0.75):
    words = user_query.split()
    flat_titles = " ".join(corpus_titles).split()
    suggestions = []
    for word in words:
        matches = get_close_matches(word, flat_titles, n=1, cutoff=cutoff)
        suggestions.append(matches[0] if matches else word)
    return " ".join(suggestions)
