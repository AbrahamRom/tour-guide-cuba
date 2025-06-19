import streamlit as st

def render(state):
    st.header("🔎 Recuperador de Conocimiento")
    consulta = st.text_input("¿Qué deseas saber sobre Cuba?", key="rag_input")
    if consulta:
        # ... lógica RAG ...
        state["resultados_rag"] = [
            {"texto": "Según cuba.travel, el Malecón es un sitio emblemático de La Habana.", "fuente": "https://www.cuba.travel/"}
        ]

    for res in state.get("resultados_rag", []):
        st.info(res["texto"])
        st.markdown(f"[Ver fuente original]({res['fuente']})")
