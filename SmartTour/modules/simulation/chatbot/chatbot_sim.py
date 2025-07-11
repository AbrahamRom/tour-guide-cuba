import time
from modules.src.chatbot.bot import (
    initialize_conversation,
    chatbot_conversation,
    REQUIRED_FIELDS
)
import random
from .mock_profiles import sample_profile

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def simulate_user_response(field, profile):
    return profile.get(field, f"My {field} is unknown")

def run_chatbot_simulation(profile, language="English", model="openhermes:latest"):
    conversation = initialize_conversation(language, model)
    collected_data = {"step": 0}
    log = []

    while collected_data["step"] < len(REQUIRED_FIELDS):
        field = REQUIRED_FIELDS[collected_data["step"]]
        user_msg = simulate_user_response(field, profile)

        start = time.time()
        response = chatbot_conversation(
            user_msg,
            conversation,
            collected_data,
            language,
            model
        )
        end = time.time()

        conversation.append({"role": "user", "content": user_msg})
        conversation.append({"role": "assistant", "content": response})

        log.append({
            "field": field,
            "user_input": user_msg,
            "bot_response": response,
            "latency": round(end - start, 3),
            "value_extracted": collected_data.get(field),
            "step": collected_data["step"]
        })

    return log, collected_data

def generate_random_profile():
    # Genera un perfil aleatorio basado en sample_profile, variando los valores
    profile = {}
    for k, v in sample_profile.items():
        if isinstance(v, int):
            profile[k] = random.randint(18, 70)
        elif isinstance(v, str):
            profile[k] = v + " " + random.choice(["", "and more", "with friends", "solo", ""])
        else:
            profile[k] = v
    return profile

def profile_to_text(profile):
    # Convierte el perfil a un string para comparación
    return " ".join([str(profile.get(f, "")) for f in REQUIRED_FIELDS])

def evaluate_extraction_quality(n_runs=30):
    similarities = []
    latencies = []
    for _ in range(n_runs):
        profile = generate_random_profile()
        start = time.time()
        logs, extracted = run_chatbot_simulation(profile)
        end = time.time()
        # Convertir ambos perfiles a texto
        original_text = profile_to_text(profile)
        extracted_text = profile_to_text(extracted)
        # Vectorizar y calcular similitud por coseno
        vectorizer = TfidfVectorizer().fit([original_text, extracted_text])
        vecs = vectorizer.transform([original_text, extracted_text])
        sim = cosine_similarity(vecs[0], vecs[1])[0][0]
        similarities.append(sim)
        latencies.append(end - start)
    avg_similarity = sum(similarities) / len(similarities)
    avg_latency = sum(latencies) / len(latencies)
    return {
        "average_cosine_similarity": avg_similarity,
        "average_latency": avg_latency,
        "all_similarities": similarities,
        "all_latencies": latencies
    }
