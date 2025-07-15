#!/usr/bin/env python3
"""
Script para verificar y configurar Ollama para el proyecto SmartTour Cuba.
"""

import requests
import sys
import os


def check_ollama_status():
    """Verifica si Ollama está ejecutándose y disponible."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            return True, models
        else:
            return False, []
    except requests.exceptions.ConnectionError:
        return False, []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False, []


def main():
    print("🔍 Verificando estado de Ollama...")
    print("=" * 50)

    is_available, models = check_ollama_status()

    if is_available:
        print("✅ Ollama está ejecutándose correctamente!")
        print(f"📦 Modelos disponibles: {len(models)}")

        if models:
            print("\nModelos instalados:")
            for model in models:
                name = model.get("name", "Desconocido")
                size = model.get("size", 0)
                size_mb = size / (1024 * 1024) if size > 0 else 0
                print(f"  • {name} ({size_mb:.1f} MB)")
        else:
            print("⚠️  No hay modelos instalados.")
            print("\n📝 Para instalar un modelo recomendado, ejecuta:")
            print("   ollama pull llama3.2:3b")
            print("   ollama pull gemma:2b")

    else:
        print("❌ Ollama no está disponible")
        print("\n🔧 Pasos para instalar y configurar Ollama:")
        print("1. Descarga Ollama desde: https://ollama.ai")
        print("2. Instala la aplicación en tu sistema")
        print("3. Abre una terminal y ejecuta: ollama serve")
        print("4. En otra terminal, descarga un modelo: ollama pull llama3.2:3b")
        print("5. Verifica la instalación ejecutando este script nuevamente")

        print("\n💡 Modelos recomendados (de menor a mayor tamaño):")
        print("   • ollama pull gemma:2b        # Muy ligero, ~1.7GB")
        print("   • ollama pull llama3.2:3b     # Equilibrado, ~2GB")
        print("   • ollama pull llama3.1:8b     # Más potente, ~4.7GB")

    print("\n" + "=" * 50)
    print("ℹ️  SmartTour Cuba funcionará sin Ollama, pero sin explicaciones de IA.")

    return is_available


if __name__ == "__main__":
    ollama_available = main()
    sys.exit(0 if ollama_available else 1)
