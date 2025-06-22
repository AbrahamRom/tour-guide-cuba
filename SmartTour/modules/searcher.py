import streamlit as st
from .src.searcher.app.retriever import Retriever
from .src.searcher.app.query_corrector import suggest_query
from .src.searcher.app.utils import get_snippet

def render(state):
    # Traducciones de placeholders y textos UI
    LANGUAGES = {
        "en": {
            "name": "English",
            "search_placeholder": "Search documents...",
            "did_you_mean": "Did you mean:",
            "view_full": "🔎 View Full Document",
            "similarity": "Similarity",
            "prev": "⬅️ Prev",
            "next": "Next ➡️",
            "page": "Page {current} of {total}",
            "info": "💡 Enter a query above to start searching your documents.",
            "title": "🔍 Smart Semantic Document Search"
        },
        "es": {
            "name": "Español",
            "search_placeholder": "Buscar documentos...",
            "did_you_mean": "Quizás quiso decir:",
            "view_full": "🔎 Ver documento completo",
            "similarity": "Similitud",
            "prev": "⬅️ Anterior",
            "next": "Siguiente ➡️",
            "page": "Página {current} de {total}",
            "info": "💡 Escriba una consulta arriba para buscar en sus documentos.",
            "title": "🔍 Búsqueda Semántica Inteligente de Documentos"
        },
        "fr": {
            "name": "Français",
            "search_placeholder": "Rechercher des documents...",
            "did_you_mean": "Vouliez-vous dire :",
            "view_full": "🔎 Voir le document complet",
            "similarity": "Similarité",
            "prev": "⬅️ Précédent",
            "next": "Suivant ➡️",
            "page": "Page {current} sur {total}",
            "info": "💡 Entrez une requête ci-dessus pour rechercher dans vos documents.",
            "title": "🔍 Recherche Sémantique Intelligente de Documents"
        },
        "de": {
            "name": "Deutsch",
            "search_placeholder": "Dokumente durchsuchen...",
            "did_you_mean": "Meinten Sie:",
            "view_full": "🔎 Gesamtes Dokument anzeigen",
            "similarity": "Ähnlichkeit",
            "prev": "⬅️ Zurück",
            "next": "Weiter ➡️",
            "page": "Seite {current} von {total}",
            "info": "💡 Geben Sie oben eine Anfrage ein, um Ihre Dokumente zu durchsuchen.",
            "title": "🔍 Intelligente Semantische Dokumentsuche"
        },
        "it": {
            "name": "Italiano",
            "search_placeholder": "Cerca nei documenti...",
            "did_you_mean": "Forse intendevi:",
            "view_full": "🔎 Visualizza documento completo",
            "similarity": "Similarità",
            "prev": "⬅️ Precedente",
            "next": "Successivo ➡️",
            "page": "Pagina {current} di {total}",
            "info": "💡 Inserisci una query sopra per cercare nei tuoi documenti.",
            "title": "🔍 Ricerca Semantica Intelligente nei Documenti"
        },
        "pt": {
            "name": "Português",
            "search_placeholder": "Pesquisar documentos...",
            "did_you_mean": "Você quis dizer:",
            "view_full": "🔎 Ver documento completo",
            "similarity": "Similaridade",
            "prev": "⬅️ Anterior",
            "next": "Próximo ➡️",
            "page": "Página {current} de {total}",
            "info": "💡 Digite uma consulta acima para pesquisar seus documentos.",
            "title": "🔍 Busca Semântica Inteligente de Documentos"
        },
        "ru": {
            "name": "Русский",
            "search_placeholder": "Поиск по документам...",
            "did_you_mean": "Возможно, вы имели в виду:",
            "view_full": "🔎 Показать весь документ",
            "similarity": "Сходство",
            "prev": "⬅️ Назад",
            "next": "Далее ➡️",
            "page": "Страница {current} из {total}",
            "info": "💡 Введите запрос выше, чтобы начать поиск по вашим документам.",
            "title": "🔍 Умный Семантический Поиск Документов"
        },
        "zh": {
            "name": "中文",
            "search_placeholder": "搜索文档...",
            "did_you_mean": "你想输入的是：",
            "view_full": "🔎 查看完整文档",
            "similarity": "相似度",
            "prev": "⬅️ 上一页",
            "next": "下一页 ➡️",
            "page": "第 {current} 页，共 {total} 页",
            "info": "💡 在上方输入查询以开始搜索您的文档。",
            "title": "🔍 智能语义文档搜索"
        }
    }

    # Selección de idioma en la barra lateral
    if "lang" not in state:
        state["lang"] = "en"

    lang = st.sidebar.selectbox(
        "🌐 Language / Idioma / Langue / Sprache / Lingua / Língua / Язык / 语言",
        options=list(LANGUAGES.keys()),
        format_func=lambda k: LANGUAGES[k]["name"],
        index=list(LANGUAGES.keys()).index(state["lang"])
    )
    state["lang"] = lang
    T = LANGUAGES[lang]

    # CSS visual moderno
    st.markdown("""
    <style>
        .stTextInput > div > div > input {
            padding-left: 2.5rem;
        }
        .search-container {
            position: relative;
            margin-bottom: 1rem;
        }
        .search-icon {
            position: absolute;
            top: 50%;
            left: 10px;
            transform: translateY(-50%);
            font-size: 20px;
            color: #888;
        }
        .did-you-mean {
            margin-top: -1rem;
            margin-bottom: 1rem;
            color: #999;
        }
        .document-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.2rem;
        }
        .similarity {
            font-size: 0.9rem;
            color: #5eaaa8;
            margin-bottom: 0.5rem;
        }
        .snippet {
            color: #444;
            margin-bottom: 0.75rem;
            font-style: italic;
        }
        .card {
            background-color: #fff;
            border-radius: 1rem;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        }
    </style>
    """, unsafe_allow_html=True)

    # Estado de sesión inicial
    if "search_query" not in state:
        state["search_query"] = ""
    if "page" not in state:
        state["page"] = 0

    # UI de entrada con ícono de lupa
    st.title(T["title"])
    st.markdown('<div class="search-container"><span class="search-icon">🔍</span>', unsafe_allow_html=True)
    query = st.text_input(
        "",
        state["search_query"],
        key="input_query",
        placeholder=T["search_placeholder"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Recuperador y embeddings
    retriever = Retriever()

    # Lógica de búsqueda y navegación
    RESULTS_PER_PAGE = 5

    if query:
        corrected = suggest_query(query, [doc['title'] for doc in retriever.documents])

        if corrected != query:
            st.markdown(f'<div class="did-you-mean">{T["did_you_mean"]}</div>', unsafe_allow_html=True)
            if st.button(f"👉 {corrected}", key="correction_btn"):
                state["search_query"] = corrected
                state["page"] = 0
                st.rerun()

        results = retriever.search(query, top_k=50)

        # Paginación
        total_pages = (len(results) - 1) // RESULTS_PER_PAGE + 1
        start = state["page"] * RESULTS_PER_PAGE
        end = start + RESULTS_PER_PAGE
        current_results = results[start:end]

        for doc, score in current_results:
            with st.container():
                st.markdown(f"<div class='document-title'>{doc['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='similarity'>{T['similarity']}: {score:.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='snippet'>{get_snippet(doc['content'], query)}</div>", unsafe_allow_html=True)
                with st.expander(T["view_full"]):
                    st.markdown(doc['content'])
                st.markdown('</div>', unsafe_allow_html=True)

        # Controles de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if state["page"] > 0:
                if st.button(T["prev"]):
                    state["page"] -= 1
                    st.rerun()
        with col3:
            if state["page"] < total_pages - 1:
                if st.button(T["next"]):
                    state["page"] += 1
                    st.rerun()

        # Info de página actual
        with col2:
            st.markdown(
                f"<center>{T['page'].format(current=state['page'] + 1, total=total_pages)}</center>",
                unsafe_allow_html=True
            )

    else:
        state["page"] = 0
        st.info(T["info"])
