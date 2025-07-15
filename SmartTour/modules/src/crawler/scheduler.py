"""
Punto de entrada para el sistema de crawling automatizado
"""

import sys
import os
from pathlib import Path

# Agregar paths necesarios
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from .background_scheduler import BackgroundCrawlerScheduler


def main():
    """Ejecutar el scheduler como proceso independiente"""
    destinations_dir = project_root / "DATA" / "destinations"

    scheduler = BackgroundCrawlerScheduler(str(destinations_dir))

    try:
        scheduler.start()

        # Mantener el proceso vivo
        print("Presiona Ctrl+C para detener el scheduler...")
        while scheduler.running:
            import time

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDeteniendo scheduler...")
    finally:
        scheduler.stop()


if __name__ == "__main__":
    main()
