import threading
import time
import sys
import os
import atexit
from datetime import datetime
from typing import Optional
from .single_destination_crawler import SingleDestinationCrawler
from .crawler_state import CrawlerStateManager
from .file_manager import FileManager
from .crawler_config import CRAWLER_CONFIG


class BackgroundCrawlerScheduler:
    def __init__(self, destinations_dir: str):
        self.destinations_dir = destinations_dir
        self.state_manager = CrawlerStateManager(
            os.path.join(destinations_dir, "..", "crawler_state.json")
        )
        self.file_manager = FileManager(destinations_dir, self.state_manager)
        self.crawler: Optional[SingleDestinationCrawler] = None
        self.scheduler_thread: Optional[threading.Thread] = None
        self.running = False
        self.shutdown_flag = threading.Event()
        self.available_destinations = CRAWLER_CONFIG.get("destinations", [])

        # Registrar función de limpieza al salir (compatible con Streamlit)
        atexit.register(self._cleanup_on_exit)

    def start(self):
        """Iniciar el scheduler en segundo plano"""
        if self.running:
            print("⚠ El scheduler ya está ejecutándose")
            return

        self.running = True
        self.shutdown_flag.clear()
        print("🚀 Iniciando Background Crawler Scheduler...")
        print("⏰ Esperando 1 minuto antes del primer scraping...")

        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop, daemon=True
        )
        self.scheduler_thread.start()

        print("✅ Scheduler iniciado en segundo plano")

    def stop(self):
        """Detener el scheduler"""
        print("🛑 Deteniendo Background Crawler Scheduler...")
        self.running = False
        self.shutdown_flag.set()

        if self.crawler:
            try:
                self.crawler.close()
            except Exception as e:
                print(f"Error cerrando crawler: {e}")

        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=10)

        print("✅ Scheduler detenido")

    def _cleanup_on_exit(self):
        """Función de limpieza registrada con atexit"""
        if self.running:
            print("📡 Cerrando scheduler por finalización del programa...")
            self.stop()

    def _scheduler_loop(self):
        """Loop principal del scheduler"""
        # Esperar 1 minuto inicial
        print("⏱ Esperando 60 segundos antes del primer ciclo...")
        self._wait_interruptible(60)

        while self.running:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"\n🔄 [{current_time}] Verificando destinos pendientes...")

                # Buscar próximo destino a actualizar
                destination = self.state_manager.get_next_destination_to_update(
                    self.available_destinations
                )

                if destination:
                    print(f"📍 Destino seleccionado para actualización: {destination}")
                    self._scrape_destination(destination)
                else:
                    print(
                        "✅ No hay destinos que requieran actualización en este momento"
                    )

                # Esperar 5 minutos antes del próximo check
                print("⏰ Esperando 5 minutos hasta el próximo ciclo...")
                self._wait_interruptible(300)  # 5 minutos

            except Exception as e:
                print(f"❌ Error en scheduler loop: {e}")
                # Esperar antes de reintentar
                self._wait_interruptible(60)

    def _wait_interruptible(self, seconds: int):
        """Esperar de forma interrumpible usando shutdown_flag"""
        for _ in range(seconds):
            if self.shutdown_flag.wait(1) or not self.running:
                break

    def _scrape_destination(self, destination: str):
        """Scrappear un destino específico"""
        start_time = datetime.now()
        try:
            print(f"🎯 Iniciando scraping de '{destination}'...")

            # Marcar como scrapeando
            self.state_manager.set_scraping_status(destination, "scraping")

            # Inicializar crawler
            self.crawler = SingleDestinationCrawler()

            # Realizar scraping
            results = self.crawler.crawl_single_destination(destination)

            # Procesar resultados
            if destination in results and results[destination]:
                # Convertir ofertas a formato CSV
                hotels_data = self._convert_offers_to_csv_format(results[destination])

                success = self.file_manager.write_hotels_safely(
                    destination, hotels_data
                )

                if success:
                    self.state_manager.mark_updated(destination)
                    self.state_manager.set_scraping_status(destination, "completed")
                    duration = (datetime.now() - start_time).total_seconds()
                    print(
                        f"✅ Actualización completada para {destination} ({len(hotels_data)} hoteles, {duration:.1f}s)"
                    )
                else:
                    self.state_manager.set_scraping_status(destination, "failed")
                    print(f"❌ Error escribiendo datos para {destination}")
            else:
                self.state_manager.set_scraping_status(destination, "no_data")
                print(f"⚠ No se encontraron datos para {destination}")

        except Exception as e:
            print(f"❌ Error scrapeando {destination}: {e}")
            self.state_manager.set_scraping_status(destination, "error")
        finally:
            # Limpiar recursos
            if self.crawler:
                try:
                    self.crawler.close()
                except:
                    pass
                self.crawler = None

    def _convert_offers_to_csv_format(self, offers: list) -> list:
        """Convertir ofertas del crawler al formato CSV esperado"""
        csv_data = []
        for offer in offers:
            csv_row = {
                "name": offer.get("name", ""),
                "stars": offer.get("stars", ""),
                "address": offer.get("address", ""),
                "cadena": offer.get("cadena", ""),
                "tarifa": offer.get("tarifa", ""),
                "price": offer.get("price", ""),
                "hotel_url": offer.get("hotel_url", ""),
            }
            csv_data.append(csv_row)
        return csv_data

    def get_status(self) -> dict:
        """Obtener estado actual del scheduler"""
        return {
            "running": self.running,
            "destinations_status": self.state_manager.get_status().get(
                "scraping_status", {}
            ),
            "last_updated": self.state_manager.get_status().get("last_updated", {}),
            "blocked_files": self.state_manager.get_status().get("blocked_files", []),
            "available_destinations": self.available_destinations,
            "current_thread_alive": (
                self.scheduler_thread.is_alive() if self.scheduler_thread else False
            ),
        }

    def force_update_destination(self, destination: str) -> bool:
        """Forzar actualización de un destino específico"""
        if destination not in self.available_destinations:
            print(
                f"❌ Destino '{destination}' no está en la lista de destinos disponibles"
            )
            return False

        if self.state_manager.is_file_blocked(destination):
            print(f"⚠ El destino '{destination}' está siendo procesado actualmente")
            return False

        print(f"🔧 Forzando actualización de '{destination}'...")
        self._scrape_destination(destination)
        return True
