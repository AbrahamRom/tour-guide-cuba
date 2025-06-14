rag-tourism Workspace
=====================

This workspace contains a modular Retrieval-Augmented Generation (RAG) system for tourism-related queries.

Directory Structure:
--------------------
rag-tourism/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── ollama_interface.py
│   ├── retriever.py
│   ├── rag_engine.py
│   └── utils.py
├── ui/
│   └── streamlit_app.py
├── data/
│   └── knowledge_base.json
├── config.yaml
├── requirements.txt
└── README.md

Description:
------------
- `app/`: Core backend modules for configuration, retrieval, LLM interface, and RAG logic.
- `ui/`: Streamlit-based user interface.
- `data/`: Knowledge base and data files.
- `config.yaml`: Main configuration file.
- `requirements.txt`: Python dependencies.
- `README.md`: Project documentation.

Usage:
------
1. Install dependencies: `pip install -r requirements.txt`
2. Configure settings in `config.yaml`.
3. Run the UI: `streamlit run ui/streamlit_app.py`
