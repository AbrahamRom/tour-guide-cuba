import time
from modules.src.chatbot.bot import (
    initialize_conversation,
    chatbot_conversation,
    REQUIRED_FIELDS
)

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
