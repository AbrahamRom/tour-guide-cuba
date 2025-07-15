# Prueba de integración del sistema de crawler automático

import streamlit as st
import sys
import os

# Agregar paths
sys.path.append(os.path.dirname(__file__))

from state import (
    initialize_background_crawler,
    get_crawler_status,
    stop_background_crawler,
)


def test_crawler_integration():
    """Probar la integración del crawler con Streamlit"""
    st.title("🧪 Test de Integración del Crawler")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Inicializar Crawler"):
            with st.spinner("Inicializando..."):
                result = initialize_background_crawler()
                if result:
                    st.success("✅ Crawler inicializado correctamente")
                else:
                    st.error("❌ Error inicializando crawler")

    with col2:
        if st.button("📊 Obtener Estado"):
            status = get_crawler_status()
            st.json(status)

    with col3:
        if st.button("🛑 Detener Crawler"):
            stop_background_crawler()
            st.info("Crawler detenido")

    st.divider()

    # Auto-status
    try:
        status = get_crawler_status()
        if status.get("running"):
            st.success("✅ Sistema funcionando correctamente")

            # Mostrar métricas básicas
            if status.get("available_destinations"):
                st.write(
                    f"📍 Destinos configurados: {len(status['available_destinations'])}"
                )

            if status.get("blocked_files"):
                st.write(f"🔒 Archivos bloqueados: {len(status['blocked_files'])}")
        else:
            st.warning("⚠️ Sistema no está activo")
    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="Test Crawler", page_icon="🧪")
    test_crawler_integration()
