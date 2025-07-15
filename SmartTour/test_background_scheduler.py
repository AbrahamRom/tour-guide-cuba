#!/usr/bin/env python3
"""
Script de prueba para verificar que el BackgroundCrawlerScheduler
funciona correctamente sin usar señales.
"""

import sys
import os
import time

# Añadir el directorio padre al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_background_scheduler():
    """Probar el background scheduler sin Streamlit"""
    try:
        from SmartTour.modules.src.crawler.background_scheduler import (
            BackgroundCrawlerScheduler,
        )

        destinations_dir = os.path.join(
            os.path.dirname(__file__), "DATA", "destinations"
        )

        # Crear directorio si no existe
        os.makedirs(destinations_dir, exist_ok=True)

        print("🧪 Iniciando prueba del BackgroundCrawlerScheduler...")

        # Crear y inicializar scheduler
        scheduler = BackgroundCrawlerScheduler(destinations_dir)

        print("✅ Scheduler creado correctamente")

        # Iniciar scheduler
        scheduler.start()

        print("✅ Scheduler iniciado correctamente")

        # Obtener estado
        status = scheduler.get_status()
        print(f"📊 Estado del scheduler: {status}")

        # Esperar un poco
        print("⏰ Esperando 10 segundos...")
        time.sleep(10)

        # Detener scheduler
        print("🛑 Deteniendo scheduler...")
        scheduler.stop()

        print("✅ Prueba completada exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_background_scheduler()
    sys.exit(0 if success else 1)
