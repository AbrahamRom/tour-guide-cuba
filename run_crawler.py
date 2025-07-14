"""
Script independiente para ejecutar el crawler automático
Uso: python run_crawler.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    try:
        from SmartTour.modules.src.crawler.background_scheduler import (
            BackgroundCrawlerScheduler,
        )

        # Configurar directorio de destinos
        destinations_dir = project_root / "DATA" / "destinations"

        if not destinations_dir.exists():
            print(f"❌ Error: Directorio de destinos no encontrado: {destinations_dir}")
            print("Asegúrese de que existe el directorio DATA/destinations")
            return 1

        print("🚀 Iniciando Sistema de Crawler Automático...")
        print(f"📁 Directorio de destinos: {destinations_dir}")

        # Crear e iniciar scheduler
        scheduler = BackgroundCrawlerScheduler(str(destinations_dir))

        try:
            scheduler.start()

            print("\n" + "=" * 50)
            print("✅ Crawler automático iniciado correctamente")
            print("⏰ Ciclos de actualización cada 5 minutos")
            print("📊 Cada destino se actualiza máximo 1 vez por día")
            print("🔄 El sistema funciona en segundo plano")
            print("=" * 50)
            print("\n💡 Presiona Ctrl+C para detener el crawler...")

            # Mantener el proceso vivo
            import time

            while scheduler.running:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Deteniendo crawler...")
        except Exception as e:
            print(f"❌ Error durante ejecución: {e}")
        finally:
            scheduler.stop()
            print("✅ Crawler detenido correctamente")

    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print(
            "Asegúrese de estar en el directorio correcto y que todos los módulos estén disponibles"
        )
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
