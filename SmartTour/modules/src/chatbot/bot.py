import sys
import os
import json
import re
from jsonschema import validate, ValidationError
from ..rag.app.ollama_interface import OllamaClient

ollama_client = OllamaClient()
OLLAMA_MODEL = "openhermes:latest"

REQUIRED_FIELDS = [
    "name", "age", "travel_interests", "places_to_visit",
    "budget", "travel_duration", "medical_conditions", "additional_preferences"
]

data_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
        "travel_interests": {"type": "string"},
        "places_to_visit": {"type": "string"},
        "budget": {"type": "string"},
        "travel_duration": {"type": "string"},
        "medical_conditions": {"type": "string"},
        "additional_preferences": {"type": "string"},
    },
    "required": REQUIRED_FIELDS
}

def ask_ollama(messages, model=OLLAMA_MODEL):
    if not messages or messages[-1]["role"] != "user":
        raise ValueError("El último mensaje debe ser del usuario.")
    prompt = messages[-1]["content"]
    chat_history = messages[:-1]
    response = ""
    for chunk in ollama_client.stream_generate(model, prompt):
        response += chunk
    return response.strip()

def generate_prompt(field, language, model):
    prompt = f"Generate a polite and natural question in {language} to ask the user about their {field}. Return only one question."
    return ask_ollama([
        {"role": "system", "content": prompt},
        {"role": "user", "content": ""}
    ], model)

def extract_json(response):
    try:
        parsed = json.loads(response)
        if isinstance(parsed, dict) and any(k in data_schema['properties'] for k in parsed):
            return parsed
    except: pass
    matches = re.findall(r'\{.*?\}', response, re.DOTALL)
    for match in matches:
        try:
            parsed = json.loads(match)
            if any(k in data_schema['properties'] for k in parsed):
                return parsed
        except: continue
    return None

def extract_field(field, user_input, language, model):
    prompt = (
        f"The user wrote: '{user_input}'. Extract only the value for the field '{field}' and return it in JSON format as: {{\"{field}\": value}}.\n"
        f"If you cannot extract it, return {{}}. Respond in {language}."
    )
    response = ask_ollama([
        {"role": "system", "content": prompt},
        {"role": "user", "content": ""}
    ], model)
    data = extract_json(response)
    if data and field in data:
        try:
            validate(instance={field: data[field]}, schema={"type": "object", "properties": {field: data_schema['properties'][field]}, "required": [field]})
            return data[field]
        except: return None
    return None

def translate(text, language, model):
    if language.lower() == "english":
        return text
    prompt = f"Translate this to {language}: {text}"
    return ask_ollama([
        {"role": "system", "content": prompt},
        {"role": "user", "content": ""}
    ], model)

def initialize_conversation(language, model):
    return [{"role": "system", "content": f"You are a friendly assistant that helps users plan travel in {language}."}]

def chatbot_conversation(user_input, conversation_history, collected_data, language, model):
    if "step" not in collected_data:
        collected_data["step"] = 0

    current_step = collected_data["step"]
    if current_step < len(REQUIRED_FIELDS):
        field = REQUIRED_FIELDS[current_step]
        value = extract_field(field, user_input, language, model)
        if value is not None:
            collected_data[field] = value
            collected_data["step"] += 1
            if collected_data["step"] < len(REQUIRED_FIELDS):
                next_field = REQUIRED_FIELDS[collected_data["step"]]
                question = generate_prompt(next_field, language, model)
                return question
            else:
                return translate("Thank you! I’ve collected all your travel preferences. You can now edit any field by typing its name followed by the new value.", language, model)
        else:
            retry = translate(f"I couldn't understand your answer for '{field}'. Could you try again, please?", language, model)
            return retry

    # Ya se recogieron todos los datos: verificar si es una edición
    user_input_lower = user_input.lower()
    for field in REQUIRED_FIELDS:
        if user_input_lower.startswith(field.lower()):
            value = extract_field(field, user_input, language, model)
            if value is not None:
                collected_data[field] = value
                return translate(f"Updated '{field}' successfully.", language, model)
            else:
                return translate(f"Sorry, I couldn't update '{field}' with that input. Please try again.", language, model)

    return translate("You’ve already completed the form. To update any field, type its name followed by the new value.", language, model)
