import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434/api"):
        self.base_url = base_url

    def list_models(self):
        resp = requests.get(f"{self.base_url}/tags")
        return [m["name"] for m in resp.json().get("models", [])]

    def stream_generate(self, model, prompt, temperature=0.7, max_tokens=512):
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": True
        }
        response = requests.post(f"{self.base_url}/generate", json=payload, stream=True)
        for line in response.iter_lines():
            if line:
                try:
                    yield line.decode("utf-8").split("data:")[-1].strip()
                except Exception:
                    continue
