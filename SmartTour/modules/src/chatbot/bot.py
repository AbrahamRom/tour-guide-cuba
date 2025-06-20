# chatbot_logic.py
import sys
import os
import json
import streamlit as st
from jsonschema import validate, ValidationError
import re
# Añade la ruta relativa para acceder al módulo 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'app' )))
# Importa OllamaClient desde la ruta correcta
from ..rag.app.ollama_interface import OllamaClient

# Inicializa el cliente Ollama
ollama_client = OllamaClient()
OLLAMA_MODEL = "openhermes:latest"  # Cambia por el modelo local que prefieras

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

def ask_ollama(messages, model=OLLAMA_MODEL):
    """
    Envía el historial de mensajes a Ollama y devuelve la respuesta completa.
    """
    # El método stream_generate espera prompt y chat_history
    # El último mensaje del usuario debe ir como prompt, el resto como chat_history
    if not messages or messages[-1]["role"] != "user":
        raise ValueError("El último mensaje debe ser del usuario.")
    prompt = messages[-1]["content"]
    chat_history = messages[:-1]
    response = ""
    for chunk in ollama_client.stream_generate(model, prompt, chat_history=chat_history):
        response += chunk
    return response.strip()

def ask_ollama_stream(prompt, model=OLLAMA_MODEL, chat_history=None):
    """
    Envía el prompt y el historial de chat a Ollama y devuelve el texto generado (streaming).
    Procesa correctamente los chunks JSON de Ollama.
    """
    response = ""
    for chunk in ollama_client.stream_generate(model, prompt, chat_history=chat_history):
        # Cada chunk puede ser un JSON con campo "response"
        try:
            data = json.loads(chunk)
            if isinstance(data, dict) and "response" in data:
                response += data["response"]
        except Exception:
            # Si no es JSON, ignora el chunk
            continue
    return response.strip()

def generate_flexible_prompt(field, language, model):
    """Genera una sola pregunta enriquecida y traducida para un campo dado."""
    base_instruction = (
        f"Please generate a friendly, natural, and slightly varied question to ask the user about their {field}. "
        "Only return ONE question, not multiple options. Only return the question itself."
    )
    if language.lower() != "english":
        base_instruction += f" Translate the question into {language}."
    response = ask_ollama([
        {"role": "system", "content": base_instruction},
        {"role": "user", "content": ""}
    ], model)
    # Si el modelo devuelve varias líneas, toma solo la primera pregunta encontrada
    if response:
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        # Busca la primera línea que termina con "?" o similar
        for line in lines:
            if "?" in line:
                return line
        return lines[0]  # fallback
    return f"Could you tell me your {field}?"

def generate_prompt(collected_data, language, model):
    for field in ["name"] + REQUIRED_FIELDS:
        if field not in collected_data:
            return field, generate_flexible_prompt(field, language, model)
    return None, translate_prompt("Thanks! I’ve collected everything I need.", language, model)

def translate_prompt(text, target_language, model):
    if target_language.lower() == "english":
        return text
    prompt = [
        {"role": "system", "content": f"Translate the following text into {target_language}."},
        {"role": "user", "content": text},
    ]
    return ask_ollama(prompt, model) or text

def extract_json_from_response(response):
    """
    Extrae el primer objeto JSON válido de la respuesta, ignorando metadatos de Ollama.
    Si la respuesta contiene un campo 'response', intenta extraer el JSON de ahí.
    """
    try:
        # Intenta parsear la respuesta completa como JSON
        parsed = json.loads(response)
        # Si tiene campo 'response'
        if isinstance(parsed, dict) and "response" in parsed:
            resp_val = parsed["response"]
            # Si el campo response es un string vacío, no hay datos útiles
            if not resp_val or not str(resp_val).strip():
                return None
            # Si el campo response parece un JSON embebido, intenta parsearlo
            try:
                resp_json = json.loads(resp_val)
                if any(k in data_schema['properties'] for k in resp_json):
                    return resp_json
            except Exception:
                # Si no es JSON, pero es texto, intenta buscar un bloque JSON dentro del string
                matches = re.findall(r'\{.*?\}', resp_val, re.DOTALL)
                for match in matches:
                    try:
                        resp_json = json.loads(match)
                        if any(k in data_schema['properties'] for k in resp_json):
                            return resp_json
                    except Exception:
                        continue
                return None
        # Si el JSON parseado ya es un objeto con campos relevantes
        if any(k in data_schema['properties'] for k in parsed):
            return parsed
    except Exception:
        pass
    # Si no es JSON válido, busca el primer bloque {...}
    matches = re.findall(r'\{.*?\}', response, re.DOTALL)
    for match in matches:
        try:
            parsed = json.loads(match)
            if any(k in data_schema['properties'] for k in parsed):
                return parsed
        except Exception:
            continue
    return None

def extract_field_value(field, user_response, language, model):
    prompt = (
        f"The user answered: '{user_response}'. "
        f"Extract only the value for '{field}' in JSON format. "
        "If the answer is not compatible or not related to the field, return an empty JSON object ({})."
    )
    if language.lower() != "english":
        prompt += f" Respond in {language}."
    response = ask_ollama([
        {"role": "system", "content": prompt},
        {"role": "user", "content": ""}
    ], model)
    # Extrae solo el JSON relevante, ignorando metadatos
    extracted = extract_json_from_response(response)
    if not extracted or field not in extracted:
        return None
    try:
        validate(instance=extracted, schema={"type": "object", "properties": {field: data_schema['properties'][field]}, "required": [field]})
        return extracted
    except (json.JSONDecodeError, ValidationError):
        return None

def try_update_fields_from_user_input(user_input, language, model):
    prompt = f"""
The user said: '{user_input}'. Identify which of the following fields they want to update and extract the new value(s) in JSON format:
{REQUIRED_FIELDS}.
Only return a JSON object with the updated fields and values. If nothing relevant is found, return an empty JSON.
"""
    response = ask_ollama([
        {"role": "system", "content": prompt},
        {"role": "user", "content": ""}
    ], model)
    try:
        parsed = json.loads(response)
        for key in list(parsed):
            if key not in data_schema['properties']:
                del parsed[key]
        return parsed
    except Exception:
        return {}

def initialize_conversation(language, model):
    # Solo la instrucción de sistema y la primera pregunta (nombre)
    return [
        {"role": "system", "content": f"You are a friendly travel assistant helping users plan their trip in {language}."}
    ]

def chatbot_conversation(user_input, conversation_history, collected_data, language, model):
    """
    Flujo de conversación tipo chat, similar al RAG: el usuario escribe, el modelo responde, se muestra todo el historial.
    """
    # Inicializa historial si está vacío
    if not conversation_history:
        conversation_history = initialize_conversation(language, model)

    # Añade el mensaje del usuario al historial
    conversation_history.append({"role": "user", "content": user_input})

    # Construye el historial para Ollama (sin el system prompt)
    ollama_history = [msg for msg in conversation_history if msg["role"] in ("user", "assistant")]

    # Prompt: el último mensaje del usuario
    prompt = user_input

    # Llama a Ollama y obtiene la respuesta (streaming)
    response = ask_ollama_stream(prompt, model=model, chat_history=ollama_history[:-1])

    # Añade la respuesta al historial
    conversation_history.append({"role": "assistant", "content": response})

    # No se recolectan datos estructurados, solo chat plano
    return response, conversation_history, collected_data
