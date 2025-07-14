import streamlit as st
import os


def get_state():
    if "state" not in st.session_state:
        st.session_state["state"] = {
            "usuario": {},
            "historial_chat": [],
            "preferencias": {},
            "recomendaciones": [],
            "itinerario": [],
            "resultados_rag": [],
            "simulacion": {},
            "notificaciones": [],
            "idioma": "Español",
            "crawler_scheduler": None,  # Nuevo campo para el scheduler
            "crawler_initialized": False,  # Flag para evitar múltiples inicializaciones
        }
    return st.session_state["state"]


def initialize_background_crawler():
    """Inicializar el crawler de fondo si no está activo"""
    state = get_state()

    # Evitar múltiples inicializaciones
    if state["crawler_initialized"] and state["crawler_scheduler"] is not None:
        return state["crawler_scheduler"]

    try:
        from modules.src.crawler.background_scheduler import BackgroundCrawlerScheduler

        destinations_dir = os.path.join(
            os.path.dirname(__file__), "DATA", "destinations"
        )

        # Crear directorio si no existe
        os.makedirs(destinations_dir, exist_ok=True)

        # Crear scheduler sin inicializar señales (compatible con Streamlit)
        scheduler = BackgroundCrawlerScheduler(destinations_dir)
        scheduler.start()

        state["crawler_scheduler"] = scheduler
        state["crawler_initialized"] = True

        print("✅ Background crawler inicializado correctamente")
        return scheduler

    except ImportError as e:
        error_msg = f"Módulos de crawler no disponibles: {e}"
        print(f"⚠️ {error_msg}")
        st.warning(f"⚠️ {error_msg}")
        return None
    except Exception as e:
        error_msg = f"Error inicializando background crawler: {e}"
        print(f"❌ {error_msg}")
        # No mostrar error en Streamlit aquí para evitar duplicados
        return None


def get_crawler_status():
    """Obtener estado del crawler de fondo"""
    state = get_state()
    if state["crawler_scheduler"]:
        try:
            return state["crawler_scheduler"].get_status()
        except Exception as e:
            st.error(f"Error obteniendo estado del crawler: {e}")
            return {"running": False, "error": str(e)}
    return {"running": False}


def stop_background_crawler():
    """Detener el crawler de fondo"""
    state = get_state()
    if state["crawler_scheduler"]:
        try:
            state["crawler_scheduler"].stop()
            state["crawler_scheduler"] = None
            state["crawler_initialized"] = False
            st.success("🛑 Crawler detenido correctamente")
        except Exception as e:
            st.error(f"Error deteniendo crawler: {e}")


def restart_background_crawler():
    """Reiniciar el crawler de fondo"""
    stop_background_crawler()
    return initialize_background_crawler()


# Función para limpiar recursos al cerrar Streamlit
def cleanup_on_exit():
    """Limpiar recursos cuando se cierra la aplicación"""
    state = get_state()
    if state["crawler_scheduler"]:
        try:
            state["crawler_scheduler"].stop()
        except:
            pass


# Registrar función de limpieza
import atexit

atexit.register(cleanup_on_exit)
