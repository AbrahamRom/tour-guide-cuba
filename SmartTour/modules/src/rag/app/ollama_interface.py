import requests
import json
from requests.exceptions import ConnectionError, RequestException


class OllamaClient:
    def __init__(self, base_url="http://localhost:11434/api"):
        self.base_url = base_url

    def is_ollama_available(self):
        """Verifica si el servidor Ollama está disponible."""
        try:
            response = requests.get(f"{self.base_url}/tags", timeout=5)
            return response.status_code == 200
        except (ConnectionError, RequestException):
            return False

    def list_models(self):
        """Lista los modelos disponibles en Ollama. Retorna lista vacía si no está disponible."""
        try:
            resp = requests.get(f"{self.base_url}/tags", timeout=5)
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except (ConnectionError, RequestException):
            return []

    def stream_generate(self, model, prompt, temperature=0.7, max_tokens=512):
        """Genera texto usando Ollama. Maneja errores de conexión."""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "num_predict": max_tokens,
                "stream": True,
            }
            response = requests.post(
                f"{self.base_url}/generate", json=payload, stream=True, timeout=30
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        yield line.decode("utf-8").split("data:")[-1].strip()
                    except Exception:
                        continue
        except (ConnectionError, RequestException) as e:
            yield f"Error: No se puede conectar a Ollama. Por favor, asegúrese de que Ollama esté ejecutándose. Detalles: {str(e)}"
