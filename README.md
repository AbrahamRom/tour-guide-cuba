# 🌴 SmartTour Cuba

> **An Intelligent, AI-Powered Tourist Guide for Cuba**

SmartTour Cuba is a comprehensive, AI-driven platform designed to provide personalized travel experiences in Cuba. Developed as an interdisciplinary project combining **Artificial Intelligence, Information Retrieval Systems, and Simulation**, it leverages state-of-the-art Large Language Models (LLMs) and optimization algorithms to act as your ultimate virtual travel assistant.

## 🤖 Core AI & LLM Features

SmartTour heavily relies on modern AI techniques to provide a seamless and intelligent user experience:

- **Local RAG (Retrieval-Augmented Generation):**
  - **Privacy-First:** Operates entirely locally without sending data to external APIs.
  - **Vector Search:** Uses **FAISS** and **MiniLM** (`all-MiniLM-L6-v2`) embeddings to perform semantic search over a rich, locally stored knowledge base (built from high-quality sources like EcuRed).
  - **Generative AI:** Integrates with **Ollama** (supporting models like *Gemma 2*, *OpenHermes*) to generate accurate, context-aware, and warmly-toned responses.
- **Intelligent Chatbot:** A multilingual conversational agent that understands natural language queries, grounds its answers in real Cuban context, and assists users interactively.
- **Smart Recommender System:** Employs NLP (Sentence Transformers) to match your textual preferences with the best tourist spots, hotels, and activities in Cuba.
- **Metaheuristic Route Planner:** Uses advanced optimization algorithms like **Ant Colony Optimization (ACO)** and **Particle Swarm Optimization (PSO)**, combined with fuzzy logic preferences, to build the perfect travel itinerary based on budget, time, and user priorities.

## ✨ Additional Features

- 🗺️ **Interactive Route Mapping:** Visualizes your customized itineraries using Folium and OpenStreetMap.
- 📚 **Dynamic Knowledge Base:** Web-scraped and parsed encyclopedia data for deep, accurate information about Cuban culture, history, geography, and travel tips.
- 🎲 **Tourism Simulator:** Simulates travel scenarios to test and refine recommendations.
- 👤 **User Management:** Keeps track of user preferences, budgets, and saved itineraries.
- 📤 **Export & Share:** Export your AI-generated travel plans.

## 🛠️ Tech Stack

- **Frontend:** Streamlit, Folium
- **AI & NLP:** Ollama, Sentence-Transformers (MiniLM), FAISS
- **Optimization:** Optuna, Metaheuristics (ACO/PSO)
- **Data Gathering:** Selenium (Web Crawler), HTML2Text, libzim
- **Language:** Python (91%+)

## 🚀 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AbrahamRom/tour-guide-cuba.git
   cd tour-guide-cuba
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the Local LLM (Ollama):**
   Ensure [Ollama](https://ollama.ai/) is installed and running on your system, then pull your preferred model:
   ```bash
   ollama pull gemma2
   # or: ollama pull openhermes
   ```

4. **Run the Application:**
   ```bash
   streamlit run SmartTour/main.py
   ```

## ⚙️ Configuration
- Edit `config.yaml` (within the RAG module) to tweak retrieval and LLM settings.
- Adjust the Knowledge Base data in `data/knowledge_base.json`.

---
*Created as part of the Computer Science program (3rd year) - Specializing in Artificial Intelligence and Simulation.*