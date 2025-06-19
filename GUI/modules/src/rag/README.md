# Sistema RAG SmartTour

Un sistema local de Recuperación Aumentada por Generación (RAG) que respeta la privacidad, utilizando:
- **FAISS + MiniLM** para recuperación de documentos
- **Ollama + LLMs** para generación
- Interfaz **Streamlit** para una interacción sencilla

## Configuración
1. `pip install -r requirements.txt`
2. Descarga un modelo local: `ollama pull openhermes`
3. Ejecuta: `streamlit run ui/streamlit_app.py`

## Personalización
- Edita `config.yaml` para los ajustes del modelo de recuperación y LLM.
- Agrega documentos en `data/knowledge_base.json`.

## Características
- Interruptor de recuperación
- Interfaz LLM solo local
- Respuestas multilingües y con tono cálido
