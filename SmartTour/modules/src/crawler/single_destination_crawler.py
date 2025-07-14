from .crawler import CubaTravelCrawler
from .crawler_config import CRAWLER_CONFIG, SELENIUM_CONFIG
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


class SingleDestinationCrawler(CubaTravelCrawler):
    def __init__(self, base_url="https://www.cuba.travel/"):
        super().__init__(base_url)

    def crawl_single_destination(self, destination: str) -> dict:
        """Crawlear un solo destino específico"""
        print(f"🔍 Iniciando scraping para: {destination}")

        try:
            self.driver.get(self.base_url)
            time.sleep(2)

            # Inyectar CSS para optimizar carga
            self._optimize_page_loading()

            # Esperar a que la página cargue
            WebDriverWait(self.driver, 60).until(
                lambda d: d.execute_script("return document.readyState")
                in ["interactive", "complete"]
            )

            wait = WebDriverWait(self.driver, 60)
            booking_box = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "booking-box-container"))
            )

            print(f"📍 Seleccionando destino: {destination}")
            # Seleccionar destino específico
            self._select_destination(wait, destination)
            self._click_buscar()

            print(f"⏳ Esperando resultados para '{destination}'...")
            
            # Esperar a que aparezcan los resultados
            if not self._wait_for_results(wait, destination):
                print(f"⚠ No se encontraron resultados para {destination}")
                return {destination: []}

            # Extraer ofertas usando el método mejorado
            offers = self.extract_offers()

            print(
                f"✅ Scraping completado para '{destination}': {len(offers)} ofertas encontradas"
            )
            return {destination: offers}

        except Exception as e:
            print(f"❌ Error durante scraping de {destination}: {e}")
            import traceback
            traceback.print_exc()
            return {destination: []}

    def _optimize_page_loading(self):
        """Optimizar carga de página deshabilitando elementos pesados"""
        try:
            # Deshabilitar videos y elementos multimedia
            self.driver.execute_script(
                """
                var style = document.createElement('style');
                style.innerHTML = `
                    video, iframe, .video-background, .ytp-cued-thumbnail-overlay-image,
                    .carousel-item img, .hero-banner img {
                        display: none !important;
                        visibility: hidden !important;
                    }
                `;
                document.head.appendChild(style);
            """
            )

            # Pausar todos los videos
            self.driver.execute_script(
                """
                var vids = document.querySelectorAll('video');
                vids.forEach(function(v) { 
                    if(v.pause) v.pause(); 
                    v.src = ""; 
                    v.load();
                });
            """
            )
        except Exception as e:
            print(f"Warning: No se pudo optimizar la carga de página: {e}")

    def _wait_for_results(self, wait, destination):
        """Esperar a que aparezcan los resultados de búsqueda"""
        try:
            # Intentar encontrar la paginación primero
            wait.until(EC.presence_of_element_located((By.ID, "Page1")))
            return True
        except Exception:
            try:
                # Si no hay paginación, buscar los contenedores de resultados
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".row.pb15"))
                )
                time.sleep(1)
                return True
            except Exception as e:
                print(f"⚠ No se encontraron resultados para {destination}: {e}")
                return False

    def extract_offers(self):
        """Extrae ofertas con la lógica correcta del crawler principal"""
        offers = []
        wait = WebDriverWait(self.driver, 60)

        try:
            total_pages = self._get_total_pages()
            print(f"📄 Total de páginas encontradas: {total_pages}")

            for page in range(1, total_pages + 1):
                print(f"📖 Procesando página {page}/{total_pages}")

                # Navegar a la página específica si hay paginación
                if total_pages > 1:
                    try:
                        page_btn = self.driver.find_element(
                            By.CSS_SELECTOR, f"#pagination-signs-bottom li[data-lp='{page}'] a"
                        )
                        self._scroll_to_element(page_btn)
                        page_btn.click()

                        # Esperar a que el contenedor de la página esté visible y tenga ofertas
                        wait.until(EC.visibility_of_element_located((By.ID, f"Page{page}")))
                        wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, f"#Page{page} .row.pb15")
                            )
                        )
                        page_content = self.driver.find_element(By.ID, f"Page{page}")
                    except Exception as e:
                        print(f"⚠ Error navegando a página {page}: {e}")
                        # Si no hay paginación, usar todo el contenido
                        page_content = self.driver
                else:
                    page_content = self.driver

                # Encontrar todas las ofertas en esta página
                offer_divs = page_content.find_elements(By.CSS_SELECTOR, ".row.pb15")
                # Filtrar solo los que están visibles
                offer_divs = [o for o in offer_divs if o.is_displayed()]

                print(f"🏨 Encontradas {len(offer_divs)} ofertas en página {page}")

                for i, offer in enumerate(offer_divs):
                    try:
                        # Extraer nombre y URL del hotel
                        name_elem = offer.find_element(
                            By.CSS_SELECTOR, ".htl-card-body h3.media-heading a"
                        )
                        name = name_elem.text.strip()
                        hotel_url = name_elem.get_attribute("href")

                        # Manejar URLs de JavaScript y construir URL válida
                        if hotel_url and hotel_url.strip().lower().startswith("javascript"):
                            hotel_url = None
                            try:
                                img_elem = offer.find_element(By.CSS_SELECTOR, ".htl-thumb img")
                                img_src = img_elem.get_attribute("data-src") or img_elem.get_attribute("src")
                                match = re.search(r"/hotel\.multimedia/[^/]+/(\d+)/Hotel/", img_src)
                                if match:
                                    hotel_id = match.group(1)
                                    hotel_url = f"https://www.cuba.travel//Hotel/Detail?propertyNumber=HT;{hotel_id}&refpoint=La_Habana&iata=HAV&checkIn=20250604&checkOut=20250605&rooms=1&adults=1&children=0&ages=0&currency=USD&tab=info"
                            except Exception:
                                pass

                        print(f"  🏨 Procesando: {name}")

                        # Extraer número de estrellas
                        stars = len(
                            offer.find_elements(
                                By.CSS_SELECTOR,
                                ".htl-card-body h3.media-heading small span.glyphicon-star",
                            )
                        )

                        # Extraer dirección
                        try:
                            address = (
                                offer.find_element(
                                    By.CSS_SELECTOR,
                                    ".description .truncateDescription span",
                                )
                                .text.strip()
                                .replace("\n", " ")
                            )
                        except Exception:
                            address = ""

                        # Extraer cadena hotelera
                        try:
                            cadena = (
                                offer.find_element(
                                    By.XPATH, ".//div[span/b[contains(text(),'Cadena:')]]"
                                )
                                .text.replace("Cadena: ", "")
                                .strip()
                            )
                        except Exception:
                            cadena = ""

                        # Extraer tarifa
                        tarifa = None
                        tarifa_selectors = [
                            ".//div[strong[contains(text(),'Tarifa:')]]/span",
                            ".//div[span/strong[contains(text(),'Tarifa:')]]/span",
                            ".//div[contains(text(),'Tarifa:')]/following-sibling::span[1]",
                            ".//span[contains(text(),'Tarifa:')]/following-sibling::span[1]",
                        ]

                        for sel in tarifa_selectors:
                            elems = offer.find_elements(By.XPATH, sel)
                            if elems:
                                tarifa = elems[0].text.strip()
                                break

                        if not tarifa:
                            elems = offer.find_elements(By.CSS_SELECTOR, ".tarifa, .rate, .tarifa-label")
                            if elems:
                                tarifa = elems[0].text.strip()

                        # Extraer precio
                        price = None
                        price_elems = offer.find_elements(By.CSS_SELECTOR, ".price")
                        if price_elems:
                            price = price_elems[0].text.strip()
                        else:
                            price_elems = offer.find_elements(By.CSS_SELECTOR, ".media-price p")
                            if price_elems:
                                price = price_elems[0].text.strip()

                        # Normalizar precio "No disponible"
                        if price and price.lower().strip() == "no disponible":
                            price = "No disponible"

                        # Crear objeto de oferta
                        offer_data = {
                            "name": name,
                            "stars": stars,
                            "address": address,
                            "cadena": cadena,
                            "tarifa": tarifa,
                            "price": price,
                            "hotel_url": hotel_url,
                        }

                        offers.append(offer_data)
                        print(f"    ✅ {name} - {stars}⭐ - {price}")

                    except Exception as e:
                        print(f"    ❌ Error extrayendo oferta {i+1} en página {page}: {e}")
                        continue

        except Exception as e:
            print(f"❌ Error general en extracción de ofertas: {e}")

        print(f"✅ Total de ofertas extraídas: {len(offers)}")
        return offers
