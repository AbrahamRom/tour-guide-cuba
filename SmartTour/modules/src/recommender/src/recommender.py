import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class Recommender:
    def __init__(self, user_profile, offers):
        self.user = user_profile
        self.offers = offers

    def rank_offers(self, top_k=5):
        vectors = np.array([o.vector for o in self.offers])
        similarities = cosine_similarity([self.user.vector], vectors)[0]
        ranked = sorted(zip(similarities, self.offers), key=lambda x: x[0], reverse=True)
        return ranked[:top_k]
