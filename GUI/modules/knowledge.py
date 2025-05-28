import streamlit as st

def render(state):
    st.header("📚 Base de Conocimiento")
    consulta = st.text_input("Buscar información (ej: museos abiertos los domingos):", key="kb_search")
    if consulta:
        # ... lógica de búsqueda semántica ...
        st.session_state["info_cards"] = [
            {"lugar": "Museo Nacional", "horario": "9:00-17:00", "descripcion": "Arte cubano e internacional."}
        ]
    for card in st.session_state.get("info_cards", []):
        with st.expander(card["lugar"]):
            st.markdown(f"**Horario:** {card['horario']}")
            st.markdown(f"**Descripción:** {card['descripcion']}")
