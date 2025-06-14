import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434/api"):
        self.base_url = base_url

    def list_models(self):
        resp = requests.get(f"{self.base_url}/tags")
        return [m["name"] for m in resp.json().get("models", [])]

    def generate(self, model, prompt, temperature=0.7, max_tokens=512):
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False
        }
        response = requests.post(f"{self.base_url}/generate", json=payload)
        return response.json()["response"].strip()
