def display_offer(offer):
    for k, v in offer.items():
        if isinstance(v, list):
            v = ", ".join(v)
        yield f"**{k.capitalize()}**: {v}"
