import streamlit as st
from state import (
    get_crawler_status,
    initialize_background_crawler,
    stop_background_crawler,
)
import pandas as pd
from datetime import datetime
import time


def render(state):
    """Función render para integración con el sistema de módulos de SmartTour"""
    show_crawler_monitor()


def show_crawler_monitor():
    """Interface completa de monitoreo del crawler para Streamlit"""
    st.header("🤖 Monitor del Crawler Automático")

    # Información inicial
    st.info(
        "📊 Este sistema mantiene actualizados los datos de hoteles automáticamente en segundo plano"
    )

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.subheader("🔍 Estado del Sistema")

    with col2:
        if st.button("🔄 Actualizar Estado", key="refresh_crawler"):
            st.rerun()

    with col3:
        if st.button("🚀 Reiniciar Crawler", key="restart_crawler"):
            with st.spinner("Reiniciando crawler..."):
                stop_background_crawler()
                time.sleep(1)
                initialize_background_crawler()
                st.success("✅ Crawler reiniciado")
                time.sleep(1)
                st.rerun()

    # Mostrar estado actual
    try:
        # Obtener estado del crawler
        status = get_crawler_status()

        # Estado general con métricas
        if status.get("running", False):
            st.success("✅ **Crawler ejecutándose en segundo plano**")

            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🟢 Estado", "Activo")
            with col2:
                thread_status = (
                    "✅ Sí" if status.get("current_thread_alive", False) else "❌ No"
                )
                st.metric("🧵 Thread Activo", thread_status)
            with col3:
                dest_count = len(status.get("available_destinations", []))
                st.metric("� Destinos", dest_count)
            with col4:
                blocked_count = len(status.get("blocked_files", []))
                st.metric("🔒 Bloqueados", blocked_count)
        else:
            st.error("❌ **Crawler no está activo**")
            st.warning("👆 El sistema de actualización automática no está funcionando")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Inicializar Crawler", key="init_crawler"):
                    with st.spinner("Inicializando crawler..."):
                        initialize_background_crawler()
                        st.success("✅ Crawler inicializado")
                        time.sleep(1)
                        st.rerun()
            with col2:
                st.info("ℹ️ El crawler actualiza los datos de hoteles cada 5 minutos")

        # Mostrar configuración de destinos
        if status.get("available_destinations"):
            with st.expander("📍 Destinos Configurados", expanded=False):
                destinations = status["available_destinations"]

                # Mostrar en columnas para mejor visualización
                cols = st.columns(3)
                for i, dest in enumerate(destinations):
                    with cols[i % 3]:
                        st.write(f"• {dest}")

        # Estado detallado de destinos
        if status.get("destinations_status"):
            st.subheader("📊 Estado Detallado por Destino")

            # Preparar datos para la tabla
            status_data = []
            current_time = datetime.now()

            for dest, info in status["destinations_status"].items():
                last_update = status.get("last_updated", {}).get(dest)

                # Calcular tiempo transcurrido
                if last_update:
                    try:
                        last_update_dt = datetime.fromisoformat(last_update)
                        time_diff = current_time - last_update_dt
                        hours_ago = round(time_diff.total_seconds() / 3600, 1)

                        if hours_ago < 1:
                            time_display = f"{round(time_diff.total_seconds() / 60)}m"
                        elif hours_ago < 24:
                            time_display = f"{hours_ago}h"
                        else:
                            days_ago = round(hours_ago / 24, 1)
                            time_display = f"{days_ago}d"
                    except:
                        time_display = "Error"
                else:
                    time_display = "Nunca"

                # Mapear estado a emoji y color
                status_info = {
                    "scraping": ("🔄", "En Proceso"),
                    "completed": ("✅", "Completado"),
                    "failed": ("❌", "Fallido"),
                    "error": ("⚠️", "Error"),
                    "no_data": ("📭", "Sin Datos"),
                }.get(info.get("status", "unknown"), ("❓", "Desconocido"))

                status_data.append(
                    {
                        "Destino": dest,
                        "Estado": f"{status_info[0]} {status_info[1]}",
                        "Última Actualización": time_display,
                        "Timestamp": (
                            info.get("timestamp", "")[:19]
                            if info.get("timestamp")
                            else ""
                        ),
                    }
                )

            if status_data:
                # Mostrar tabla con datos
                df = pd.DataFrame(status_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Métricas resumidas
                completed = sum(1 for d in status_data if "✅" in d["Estado"])
                failed = sum(
                    1 for d in status_data if "❌" in d["Estado"] or "⚠️" in d["Estado"]
                )
                in_progress = sum(1 for d in status_data if "🔄" in d["Estado"])
                no_data = sum(1 for d in status_data if "📭" in d["Estado"])

                st.subheader("📈 Resumen de Estados")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("✅ Completados", completed)
                with col2:
                    st.metric("❌ Con Errores", failed)
                with col3:
                    st.metric("🔄 En Proceso", in_progress)
                with col4:
                    st.metric("📭 Sin Datos", no_data)

        # Archivos bloqueados
        blocked_files = status.get("blocked_files", [])
        if blocked_files:
            st.warning("🔒 **Archivos Temporalmente Bloqueados**")
            st.caption("Estos archivos están siendo actualizados en este momento:")
            for file in blocked_files:
                st.write(f"• {file}")
            st.info(
                "💡 Los archivos bloqueados volverán a estar disponibles una vez completada la actualización"
            )

        # Configuración y controles
        st.subheader("⚙️ Configuración del Sistema")

        col1, col2 = st.columns(2)

        with col1:
            st.info("📅 **Frecuencia de Actualización**")
            st.write("• Verificación cada 5 minutos")
            st.write("• Máximo 1 actualización por destino cada 24 horas")
            st.write("• Espera inicial de 1 minuto al inicio")

        with col2:
            st.info("🔧 **Funcionalidades**")
            st.write("• Ejecución en segundo plano")
            st.write("• No bloquea la aplicación principal")
            st.write("• Actualización automática de datos")
            st.write("• Gestión inteligente de recursos")

        # Auto-refresh opcional
        with st.expander("🔄 Opciones de Actualización", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                auto_refresh = st.checkbox(
                    "🔄 Auto-actualizar cada 30s", key="auto_refresh"
                )
                if auto_refresh:
                    st.info("⏰ La página se actualizará automáticamente")
                    time.sleep(30)
                    st.rerun()

            with col2:
                if st.button("🔄 Actualizar Ahora", key="manual_refresh"):
                    st.rerun()

        # Información técnica en expander
        with st.expander("🔍 Información Técnica", expanded=False):
            st.json(status)

    except Exception as e:
        st.error(f"❌ **Error obteniendo estado del crawler:** {str(e)}")

        with st.expander("🔧 Diagnóstico y Solución"):
            st.write("**Posibles causas del error:**")
            st.write("• Módulos del crawler no están correctamente instalados")
            st.write("• Problemas de permisos en el directorio DATA")
            st.write("• El sistema de archivos está bloqueado")
            st.write("• Error en la configuración de rutas")

            st.write("\n**Soluciones sugeridas:**")
            st.write("1. Reiniciar la aplicación Streamlit")
            st.write("2. Verificar que existe el directorio DATA/destinations")
            st.write("3. Verificar permisos de escritura en el proyecto")
            st.write("4. Revisar los logs del sistema")

            st.code(f"Error técnico: {e}", language="text")


# Función principal para testing independiente
def main():
    st.set_page_config(page_title="Monitor Crawler", page_icon="🤖", layout="wide")

    st.title("🤖 Monitor del Sistema de Crawler Automático")
    show_crawler_monitor()


if __name__ == "__main__":
    main()
