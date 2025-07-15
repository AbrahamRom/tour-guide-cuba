import threading
import time
import os
import csv
from pathlib import Path
from typing import List
from .crawler_state import CrawlerStateManager


class FileManager:
    def __init__(self, destinations_dir: str, state_manager: CrawlerStateManager):
        self.destinations_dir = Path(destinations_dir)
        self.state_manager = state_manager
        self.write_locks = {}
        self.lock = threading.RLock()

    def can_read_file(self, destination: str) -> bool:
        """Verificar si se puede leer el archivo (siempre True, excepto durante escritura)"""
        filename = f"{destination.lower().replace(' ', '_')}.csv"
        file_path = self.destinations_dir / filename

        # Verificar si existe el archivo
        if not file_path.exists():
            return False

        # El archivo es legible a menos que esté siendo escrito en este momento
        with self.lock:
            return filename not in self.write_locks

    def acquire_write_lock(self, destination: str) -> bool:
        """Adquirir lock de escritura para un destino"""
        filename = f"{destination.lower().replace(' ', '_')}.csv"

        with self.lock:
            if filename in self.write_locks:
                return False

            self.write_locks[filename] = threading.current_thread().ident
            self.state_manager.block_file(destination)
            return True

    def release_write_lock(self, destination: str):
        """Liberar lock de escritura"""
        filename = f"{destination.lower().replace(' ', '_')}.csv"

        with self.lock:
            if filename in self.write_locks:
                del self.write_locks[filename]
            self.state_manager.unblock_file(destination)

    def write_hotels_safely(self, destination: str, hotels_data: List[dict]) -> bool:
        """Escribir datos de hoteles de forma segura"""
        if not self.acquire_write_lock(destination):
            print(f"No se pudo adquirir lock de escritura para {destination}")
            return False

        try:
            filename = f"{destination.lower().replace(' ', '_')}.csv"
            file_path = self.destinations_dir / filename

            # Crear directorio si no existe
            self.destinations_dir.mkdir(parents=True, exist_ok=True)

            # Escribir CSV
            if hotels_data:
                with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                    fieldnames = hotels_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(hotels_data)
                print(
                    f"✓ Archivo {filename} actualizado con {len(hotels_data)} hoteles"
                )
            else:
                # Crear archivo vacío si no hay datos con headers correctos
                with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(
                        ["name", "stars", "address", "cadena", "tarifa", "price", "hotel_url"]
                    )
                print(f"⚠ Archivo {filename} creado vacío (no se encontraron datos)")

            return True

        except Exception as e:
            print(f"Error escribiendo archivo para {destination}: {e}")
            return False
        finally:
            self.release_write_lock(destination)

    def read_hotels_safely(self, destination: str) -> List[dict]:
        """Leer hoteles de forma segura"""
        if not self.can_read_file(destination):
            print(
                f"No se puede leer archivo para {destination} (bloqueado o no existe)"
            )
            return []

        try:
            filename = f"{destination.lower().replace(' ', '_')}.csv"
            file_path = self.destinations_dir / filename

            hotels = []
            with open(file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                hotels = list(reader)

            return hotels
        except Exception as e:
            print(f"Error leyendo archivo para {destination}: {e}")
            return []
