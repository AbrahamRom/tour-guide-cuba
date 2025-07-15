import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set, Optional


class CrawlerStateManager:
    def __init__(self, state_file: str = "crawler_state.json"):
        self.state_file = Path(state_file)
        self.lock = threading.RLock()
        self._state = self._load_state()

    def _load_state(self) -> dict:
        """Cargar estado desde archivo"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    # Convertir listas a sets para blocked_files
                    if "blocked_files" in state and isinstance(
                        state["blocked_files"], list
                    ):
                        state["blocked_files"] = set(state["blocked_files"])
                    return state
            except Exception as e:
                print(f"Error cargando estado: {e}")

        return {
            "destinations": {},
            "blocked_files": set(),
            "last_updated": {},
            "scraping_status": {},
        }

    def _save_state(self):
        """Guardar estado a archivo"""
        try:
            # Convertir sets a listas para JSON
            state_copy = self._state.copy()
            state_copy["blocked_files"] = list(state_copy["blocked_files"])

            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state_copy, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando estado: {e}")

    def is_file_blocked(self, destination: str) -> bool:
        """Verificar si un archivo está bloqueado"""
        with self.lock:
            filename = f"{destination.lower().replace(' ', '_')}.csv"
            return filename in self._state.get("blocked_files", set())

    def block_file(self, destination: str):
        """Bloquear archivo durante modificación"""
        with self.lock:
            filename = f"{destination.lower().replace(' ', '_')}.csv"
            if "blocked_files" not in self._state:
                self._state["blocked_files"] = set()
            self._state["blocked_files"].add(filename)
            self._save_state()

    def unblock_file(self, destination: str):
        """Desbloquear archivo después de modificación"""
        with self.lock:
            filename = f"{destination.lower().replace(' ', '_')}.csv"
            if "blocked_files" in self._state:
                self._state["blocked_files"].discard(filename)
            self._save_state()

    def needs_update(self, destination: str) -> bool:
        """Verificar si un destino necesita actualización (>24h)"""
        with self.lock:
            last_update = self._state.get("last_updated", {}).get(destination)
            if not last_update:
                return True

            try:
                last_update_time = datetime.fromisoformat(last_update)
                return datetime.now() - last_update_time > timedelta(hours=24)
            except Exception:
                return True

    def mark_updated(self, destination: str):
        """Marcar destino como actualizado"""
        with self.lock:
            if "last_updated" not in self._state:
                self._state["last_updated"] = {}
            self._state["last_updated"][destination] = datetime.now().isoformat()
            self._save_state()

    def set_scraping_status(self, destination: str, status: str):
        """Establecer estado de scraping para un destino"""
        with self.lock:
            if "scraping_status" not in self._state:
                self._state["scraping_status"] = {}
            self._state["scraping_status"][destination] = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
            }
            self._save_state()

    def get_next_destination_to_update(
        self, available_destinations: list
    ) -> Optional[str]:
        """Obtener próximo destino que necesita actualización"""
        with self.lock:
            for destination in available_destinations:
                status_info = self._state.get("scraping_status", {}).get(
                    destination, {}
                )
                current_status = status_info.get("status")

                # No procesar si está actualmente scrapeando
                if current_status == "scraping":
                    continue

                # No procesar si el archivo está bloqueado
                if self.is_file_blocked(destination):
                    continue

                # Verificar si necesita actualización regular (más de 24h)
                needs_regular_update = self.needs_update(destination)

                # Verificar si es un destino sin datos/error que debería reintentarse (más de 7 días)
                should_retry = self.should_retry_destination(destination)

                # Procesar si necesita actualización regular O si debería reintentarse
                if needs_regular_update or should_retry:
                    return destination

            return None

    def get_status(self) -> dict:
        """Obtener estado completo del sistema"""
        with self.lock:
            return {
                "destinations": self._state.get("destinations", {}),
                "blocked_files": list(self._state.get("blocked_files", set())),
                "last_updated": self._state.get("last_updated", {}),
                "scraping_status": self._state.get("scraping_status", {}),
            }

    def is_destination_completed_no_data(self, destination: str) -> bool:
        """Verificar si un destino fue marcado como completado sin datos"""
        with self.lock:
            status_info = self._state.get("scraping_status", {}).get(destination, {})
            return status_info.get("status") == "completed_no_data"

    def is_destination_completed_error(self, destination: str) -> bool:
        """Verificar si un destino fue marcado como completado con error"""
        with self.lock:
            status_info = self._state.get("scraping_status", {}).get(destination, {})
            return status_info.get("status") == "completed_error"

    def should_retry_destination(self, destination: str) -> bool:
        """Verificar si un destino debería ser reintentado (pasaron más de 7 días desde el último intento sin datos/error)"""
        with self.lock:
            status_info = self._state.get("scraping_status", {}).get(destination, {})
            status = status_info.get("status")

            # Si no es un estado de error o sin datos, usar la lógica normal
            if status not in ["completed_no_data", "completed_error"]:
                return False

            # Si es error o sin datos, verificar si han pasado más de 7 días
            timestamp = status_info.get("timestamp")
            if not timestamp:
                return True

            try:
                last_attempt = datetime.fromisoformat(timestamp)
                return datetime.now() - last_attempt > timedelta(days=1)
            except Exception:
                return True
