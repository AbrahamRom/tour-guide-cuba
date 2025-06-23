import os
import json

def load_all_profiles(profile_dir="data/profiles"):
    profiles = []
    for f in os.listdir(profile_dir):
        if f.endswith(".json"):
            with open(os.path.join(profile_dir, f), "r", encoding="utf-8") as file:
                profiles.append(json.load(file))
    return profiles
