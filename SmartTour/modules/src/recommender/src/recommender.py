import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class Recommender:
    def __init__(self, user_profile, offers):
        self.user = user_profile
        # Filtrar solo ofertas con vector válido
        self.offers = [o for o in offers if o.vector is not None]

    def rank_offers(self, top_k=20):
        if not self.offers:
            return []

        vectors = np.array([o.vector for o in self.offers])

        # Asegurar que es una matriz 2D
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        similarities = cosine_similarity([self.user.vector], vectors)[0]
        ranked = sorted(zip(similarities, self.offers), key=lambda x: x[0], reverse=True)
        return ranked[:top_k]
