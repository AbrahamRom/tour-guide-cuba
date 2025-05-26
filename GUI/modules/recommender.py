import streamlit as st

def render(state):
    st.header("✨ Recomendaciones Personalizadas")
    with st.expander("Perfil del Usuario"):
        state["preferencias"]["tipo"] = st.selectbox("Tipo de turismo", ["Cultural", "Playa", "Aventura"])
        state["preferencias"]["presupuesto"] = st.slider("Presupuesto ($USD)", 100, 5000, 1000)
        state["preferencias"]["duracion"] = st.slider("Duración (días)", 1, 30, 7)

    if st.button("Obtener recomendaciones"):
        # ... lógica de recomendador ...
        state["recomendaciones"] = [
            {"nombre": "La Habana Vieja", "categoria": "Cultural"},
            {"nombre": "Varadero", "categoria": "Playa"},
        ]

    st.subheader("Sugerencias")
    for rec in state.get("recomendaciones", []):
        with st.container():
            st.markdown(f"**{rec['nombre']}** ({rec['categoria']})")
            col1, col2 = st.columns(2)
            with col1:
                st.button("👍 Me gusta", key=f"like_{rec['nombre']}")
            with col2:
                st.button("👎 No me interesa", key=f"dislike_{rec['nombre']}")
