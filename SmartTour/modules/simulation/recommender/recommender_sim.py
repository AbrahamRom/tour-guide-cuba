# simulator/recommender_sim.py
import json
import os
from modules.src.recommender.src.user_profile import UserProfile
from modules.src.recommender.src.offer_loader import load_offers_from_directory
from modules.src.recommender.src.recommender import Recommender


def simulate_recommendation(profile_path, offers_dir="../DATA", top_k=5):
    with open(profile_path, "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    user_profile = UserProfile(profile_data)
    offers = load_offers_from_directory(offers_dir)
    recommender = Recommender(user_profile, offers)
    ranked = recommender.rank_offers(top_k=top_k)

    return {
        "profile_name": os.path.basename(profile_path),
        "num_offers": len(offers),
        "recommendations": [
            {
                "title": o.raw.get("name") or o.raw.get("title"),
                "score": round(score, 3),
                "details": o.raw
            }
            for score, o in ranked
        ]
    }
