# chatbot_logic.py
import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

load_dotenv()

# Configuración para OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"

REQUIRED_FIELDS = [
    "name", "age", "travel_interests", "places_to_visit",
    "budget", "travel_duration", "medical_conditions", "additional_preferences"
]

# Esquema para validar los datos extraídos
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

def ask_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openrouter.ai/",
        "X-Title": "tour-guide-cuba-bot",
    }
    data = {"model": OPENROUTER_MODEL, "messages": messages}
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error de conexión con OpenRouter: {e}")
        return ""

def generate_flexible_prompt(field, language):
    """Genera una sola pregunta enriquecida y traducida para un campo dado."""
    base_instruction = (
        f"Please generate a friendly, natural, and slightly varied question to ask the user about their {field}. "
        "Only return ONE question, not multiple options. Only return the question itself."
    )
    if language.lower() != "english":
        base_instruction += f" Translate the question into {language}."
    response = ask_openrouter([
        {"role": "system", "content": base_instruction}
    ])
    # Si el modelo devuelve varias líneas, toma solo la primera pregunta encontrada
    if response:
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        # Busca la primera línea que termina con "?" o similar
        for line in lines:
            if "?" in line:
                return line
        return lines[0]  # fallback
    return f"Could you tell me your {field}?"

def generate_prompt(collected_data, language):
    for field in ["name"] + REQUIRED_FIELDS:
        if field not in collected_data:
            return field, generate_flexible_prompt(field, language)
    return None, translate_prompt("Thanks! I’ve collected everything I need.", language)

def translate_prompt(text, target_language):
    if target_language.lower() == "english":
        return text
    prompt = [
        {"role": "system", "content": f"Translate the following text into {target_language}."},
        {"role": "user", "content": text},
    ]
    return ask_openrouter(prompt) or text

def extract_field_value(field, user_response, language="English"):
    prompt = (
        f"The user answered: '{user_response}'. "
        f"Extract only the value for '{field}' in JSON format. "
        "If the answer is not compatible or not related to the field, return an empty JSON object ({})."
    )
    if language.lower() != "english":
        prompt += f" Respond in {language}."
    response = ask_openrouter([{"role": "system", "content": prompt}])
    try:
        extracted = json.loads(response)
        # Si el modelo devuelve un objeto vacío o el campo no está presente, es respuesta incompatible
        if not extracted or field not in extracted:
            return None
        validate(instance=extracted, schema={"type": "object", "properties": {field: data_schema['properties'][field]}, "required": [field]})
        return extracted
    except (json.JSONDecodeError, ValidationError):
        return None

def try_update_fields_from_user_input(user_input, language):
    prompt = f"""
The user said: '{user_input}'. Identify which of the following fields they want to update and extract the new value(s) in JSON format:
{REQUIRED_FIELDS}.
Only return a JSON object with the updated fields and values. If nothing relevant is found, return an empty JSON.
"""
    response = ask_openrouter([{"role": "system", "content": prompt}])
    try:
        parsed = json.loads(response)
        for key in list(parsed):
            if key not in data_schema['properties']:
                del parsed[key]
        return parsed
    except Exception:
        return {}

def initialize_conversation(language):
    # Solo la instrucción de sistema y la primera pregunta (nombre)
    return [
        {"role": "system", "content": f"You are a friendly travel assistant helping users plan their trip in {language}."},
        {"role": "assistant", "content": generate_flexible_prompt("name", language)},
    ]

def chatbot_conversation(user_input, conversation_history, collected_data, language):
    # Si la conversación está vacía (solo system y pregunta de nombre), muestra la pregunta de nombre
    if len(conversation_history) == 2 and not user_input:
        return conversation_history[-1]["content"], conversation_history, collected_data

    # Intentar actualizar datos existentes si ya fueron completados
    if all(field in collected_data for field in REQUIRED_FIELDS):
        possible_updates = try_update_fields_from_user_input(user_input, language)
        if possible_updates:
            collected_data.update(possible_updates)
            confirmation = f"Updated data: {json.dumps(possible_updates, indent=2)}"
            confirmation = translate_prompt(confirmation, language)
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": confirmation})
            return confirmation, conversation_history, collected_data

    # Fase de recolección inicial de datos
    last_field, next_question = generate_prompt(collected_data, language)

    if last_field and user_input:
        update = extract_field_value(last_field, user_input, language)
        if update is not None:
            collected_data.update(update)
            last_field, next_question = generate_prompt(collected_data, language)
        else:
            # Respuesta incompatible, reintentar la pregunta
            error_msg = {
                "english": "Sorry, your answer was not compatible with the requested information. Please try again and provide a valid answer.",
                "spanish": "Lo siento, tu respuesta no fue compatible con la información solicitada. Por favor, intenta de nuevo y proporciona una respuesta válida.",
                "french": "Désolé, votre réponse n'était pas compatible avec l'information demandée. Veuillez réessayer et fournir une réponse valide.",
                "german": "Entschuldigung, Ihre Antwort war nicht kompatibel mit der angeforderten Information. Bitte versuchen Sie es erneut und geben Sie eine gültige Antwort an.",
                "italian": "Spiacente, la tua risposta non era compatibile con le informazioni richieste. Per favore riprova e fornisci una risposta valida.",
                "portuguese": "Desculpe, sua resposta não foi compatível com a informação solicitada. Por favor, tente novamente e forneça uma resposta válida."
            }
            lang_key = language.lower()
            msg = error_msg.get(lang_key, error_msg["english"])
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": msg})
            # Repite la misma pregunta
            conversation_history.append({"role": "assistant", "content": next_question})
            return f"{msg}\n\n{next_question}", conversation_history, collected_data

    if next_question:
        if user_input:
            conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": next_question})
        return next_question, conversation_history, collected_data

    summary = "Thanks! Here's a summary of your travel preferences:\n" + json.dumps(collected_data, indent=2)
    summary = translate_prompt(summary, language)
    if user_input:
        conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": summary})
    return summary, conversation_history, collected_data
