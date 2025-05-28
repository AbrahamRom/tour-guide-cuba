# chatbot_logic.py
import openai
import os
import json

# Replace with your actual API key or environment variable
openai.api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

REQUIRED_FIELDS = [
    "name", "age", "travel_interests", "places_to_visit",
    "budget", "travel_duration", "medical_conditions", "additional_preferences"
]

def translate_prompt(text, target_language):
    if target_language.lower() == "english":
        return text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Translate the following text into {target_language}."},
                {"role": "user", "content": text}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return text  # fallback to original if error occurs

def generate_prompt(collected_data, language):
    missing_fields = [field for field in REQUIRED_FIELDS if field not in collected_data]
    if not missing_fields:
        return None, translate_prompt("Thanks! I’ve collected everything I need.", language)

    friendly_names = {
        "name": "your name",
        "age": "your age",
        "travel_interests": "what kind of travel you enjoy (e.g., beach, nature, excursions)",
        "places_to_visit": "specific places you want to visit",
        "budget": "your travel budget",
        "travel_duration": "how long you plan to travel",
        "medical_conditions": "any medical conditions we should be aware of",
        "additional_preferences": "any other preferences or needs"
    }

    question = f"Could you tell me {friendly_names[missing_fields[0]]}?"
    return missing_fields[0], translate_prompt(question, language)

def update_data_from_response(field, response):
    if not response:
        return None
    return {field: response.strip()}

def ask_openai(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"I'm having trouble reaching the language model. Please try again later. ({e})"

def initialize_conversation(language):
    return [
        {"role": "system", "content": f"You are a friendly travel assistant helping users plan their trip in {language}."},
        {"role": "assistant", "content": translate_prompt("Hi there! I’m your travel assistant. Let’s plan your trip together.", language)}
    ]

def chatbot_conversation(user_input, conversation_history, collected_data, language):
    last_field, next_question = generate_prompt(collected_data, language)

    if last_field and user_input:
        update = update_data_from_response(last_field, user_input)
        collected_data.update(update)
        last_field, next_question = generate_prompt(collected_data, language)

    if next_question:
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": next_question})
        return next_question, conversation_history, collected_data
    else:
        final_message = "Thanks! Here's a summary of your travel preferences: \n" + json.dumps(collected_data, indent=2)
        final_message = translate_prompt(final_message, language)
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": final_message})
        return final_message, conversation_history, collected_data
