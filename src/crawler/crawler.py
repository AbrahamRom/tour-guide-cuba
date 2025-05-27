from .crawler_config import CRAWLER_CONFIG, SELENIUM_CONFIG
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import re
import chromedriver_autoinstaller
import tempfile
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CubaTravelCrawler:
    def __init__(self, base_url="https://www.cuba.travel/"):
        self.base_url = base_url
        self.config = CRAWLER_CONFIG
        self.selenium_config = SELENIUM_CONFIG
        self.driver = self._init_driver()
        self.disallow_patterns = self._compile_disallow_patterns()
        self.crawl_delay = self._get_crawl_delay()

    def _init_driver(self):
        options = Options()
        self.temp_user_data_dir = tempfile.TemporaryDirectory()
        if self.selenium_config["headless"]:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={self.selenium_config['window_size']}")
        options.add_argument(f"--user-agent={self.selenium_config['user_agent']}")
        options.add_argument(f"--user-data-dir={self.temp_user_data_dir.name}")
        options.page_load_strategy = "none"
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--ignore-ssl-errors")
        # Añadir preferencias desde selenium_config
        prefs = self.selenium_config.get("prefs", {})
        if self.selenium_config["download_dir"]:
            prefs["download.default_directory"] = self.selenium_config["download_dir"]
        if prefs:
            options.add_experimental_option("prefs", prefs)

        service = Service(
            "C:\\Descargas\\Utils\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
        )
        driver = webdriver.Chrome(service=service, options=options)
        # try:
        #     driver = webdriver.Chrome(options=options)
        # except Exception as e:
        #     # Si falla, intenta instalar chromedriver-autoinstaller y reintenta
        #     chromedriver_autoinstaller.install()
        #     driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(self.selenium_config["implicit_wait"])
        # driver.set_page_load_timeout(self.selenium_config["page_load_timeout"])
        return driver

    def _compile_disallow_patterns(self):
        patterns = []
        for pattern in self.config["user_agents"]["*"]["disallow"]:
            # Convert robots.txt wildcards to regex
            regex = re.escape(pattern).replace(r"\*", ".*")
            patterns.append(re.compile(regex))
        return patterns

    def _get_crawl_delay(self):
        delay = self.config["user_agents"]["*"].get("crawl_delay")
        return delay if delay is not None else 1

    def is_allowed(self, url):
        path = url.replace(self.base_url, "/")
        for pattern in self.disallow_patterns:
            if pattern.search(path):
                return False
        return True

    def _scroll_to_element(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        time.sleep(0.5)

    def _select_destination(self, wait, destination):
        # Esperar a que el input de búsqueda sea clickable y hacer scroll hasta él
        input_box = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "multiselect"))
        )
        self._scroll_to_element(input_box)
        try:
            input_box.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", input_box)
        # Esperar y seleccionar la opción de destino (más robusto)
        # Buscar la opción por texto exacto dentro del span interior
        option_xpath = f"//span[contains(@class, 'multiselect__option') and span[normalize-space(text())='{destination}']]"
        # Si no la encuentra, intentar buscar por contiene (para casos como 'Santiago')
        try:
            option_elem = wait.until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
        except Exception:
            # Fallback: buscar por contiene
            option_xpath = f"//span[contains(@class, 'multiselect__option') and contains(span/text(), '{destination}') ]"
            option_elem = wait.until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
        self._scroll_to_element(option_elem)
        try:
            option_elem.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", option_elem)
        print(f"Opción '{destination}' seleccionada.")

    def _click_buscar(self):
        buscar_btn = self.driver.find_element(
            By.XPATH,
            "//button[contains(@class, 'btn-primary') and normalize-space(text())='Buscar']",
        )
        buscar_btn.click()
        print("Botón 'Buscar' pulsado.")

    def _get_total_pages(self):
        """Devuelve el número total de páginas de resultados en la paginación."""
        try:
            pagination = self.driver.find_element(By.ID, "pagination-signs-bottom")
            page_items = pagination.find_elements(
                By.CSS_SELECTOR, "ul.pagination li[data-lp]"
            )
            # Filtrar solo los que tienen número de página
            page_numbers = [
                int(li.get_attribute("data-lp"))
                for li in page_items
                if li.get_attribute("data-lp").isdigit()
            ]
            if page_numbers:
                return max(page_numbers)
            return 1
        except Exception:
            return 1

    def extract_offers(self):
        from selenium.webdriver.common.by import By

        offers = []
        wait = WebDriverWait(self.driver, 60)
        try:
            total_pages = self._get_total_pages()
            for page in range(1, total_pages + 1):
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
                offer_divs2 = page_content.find_elements(By.CSS_SELECTOR, ".row.pb15")
                # Filtrar solo los que están visibles
                offer_divs2 = [o for o in offer_divs2 if o.is_displayed()]
                for offer in offer_divs2:
                    try:
                        # Nombre
                        name = offer.find_element(
                            By.CSS_SELECTOR, ".htl-card-body h3.media-heading a"
                        ).text.strip()
                        print(f"Procesando oferta: {name}")
                        # Estrellas
                        stars = len(
                            offer.find_elements(
                                By.CSS_SELECTOR,
                                ".htl-card-body h3.media-heading small span.glyphicon-star",
                            )
                        )
                        # print(f"Estrellas: {stars}")
                        # Dirección
                        address = (
                            offer.find_element(
                                By.CSS_SELECTOR,
                                ".description .truncateDescription span",
                            )
                            .text.strip()
                            .replace("\n", " ")
                        )
                        # print(f"Dirección: {address}")
                        # Cadena
                        cadena = (
                            offer.find_element(
                                By.XPATH, ".//div[span/b[contains(text(),'Cadena:')]]"
                            )
                            .text.replace("Cadena: ", "")
                            .strip()
                        )
                        # print(f"Cadena: {cadena}")
                        # Tarifa (más robusto)
                        tarifa = None
                        # Probar varios selectores posibles para 'tarifa' usando find_elements para evitar timeouts
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
                            # Intentar con CSS selector alternativo
                            elems = offer.find_elements(
                                By.CSS_SELECTOR, ".tarifa, .rate, .tarifa-label"
                            )
                            if elems:
                                tarifa = elems[0].text.strip()
                            else:
                                tarifa = None
                        # print(f"Tarifa: {tarifa}")
                        # Precio
                        price = None
                        price_elems = offer.find_elements(By.CSS_SELECTOR, ".price")
                        if price_elems:
                            price = price_elems[0].text.strip()
                        else:
                            price_elems = offer.find_elements(
                                By.CSS_SELECTOR, ".media-price p"
                            )
                            if price_elems:
                                price = price_elems[0].text.strip()
                            else:
                                price = None
                        # Si el precio es 'No disponible', dejarlo así y no buscar más
                        if price and price.lower().strip() == "no disponible":
                            price = "No disponible"
                        # print(f"Precio: {price}")
                        offers.append(
                            {
                                "name": name,
                                "stars": stars,
                                "address": address,
                                "cadena": cadena,
                                "tarifa": tarifa,
                                "price": price,
                            }
                        )
                    except Exception as e:
                        print(f"Error extrayendo oferta página {page}: {e}")
        except Exception as e:
            print(f"No se pudo paginar o extraer ofertas de páginas adicionales: {e}")
        print(f"Ofertas extraídas: {len(offers)}")
        return offers

    def crawl(self, urls):
        # Lista de destinos a probar, definida en la configuración
        destinos = self.config.get("destinations", ["Cuba"])

        for url in urls:
            if not self.is_allowed(url):
                print(f"Saltando (disallow): {url}")
                continue
            try:
                # self.driver.get(url)
                # WebDriverWait(self.driver, 60).until(
                #     lambda d: d.execute_script("return document.readyState")
                #     in ["interactive", "complete"]
                # )
                print(f"Crawleando: {url}")
                # wait = WebDriverWait(self.driver, 60)
                # booking_box = wait.until(
                #     EC.presence_of_element_located(
                #         (By.CLASS_NAME, "booking-box-container")
                #     )
                # )
                # print("Contenedor de reservas encontrado.")
                # self._scroll_to_element(booking_box)

                results = {}
                for destino in destinos:
                    self.driver.get(url)
                    time.sleep(2)
                    # Inyectar CSS para ocultar videos e iframes
                    self.driver.execute_script(
                        """
                        var style = document.createElement('style');
                        style.innerHTML = 'video, iframe, .video-background, .ytp-cued-thumbnail-overlay-image { display: none !important; }';
                        document.head.appendChild(style);
                    """
                    )
                    # Pausar todos los videos
                    self.driver.execute_script(
                        """
                        var vids = document.querySelectorAll('video');
                        vids.forEach(function(v) { v.pause && v.pause(); v.src = ""; });
                    """
                    )
                    WebDriverWait(self.driver, 60).until(
                        lambda d: d.execute_script("return document.readyState")
                        in ["interactive", "complete"]
                    )
                    wait = WebDriverWait(self.driver, 60)
                    booking_box = wait.until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "booking-box-container")
                        )
                    )
                    self._select_destination(wait, destino)
                    self._click_buscar()
                    print(f"Esperando resultados para '{destino}'...")
                    try:
                        wait.until(EC.presence_of_element_located((By.ID, "Page1")))
                    except Exception:
                        wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".row.pb15")
                            )
                        )
                        time.sleep(1)
                    offers = self.extract_offers()
                    results[destino] = offers
                    if offers:
                        print(f"Ofertas encontradas para '{destino}': {len(offers)}")
                    else:
                        print(f"No se encontraron ofertas para '{destino}'.")
                return results
            except Exception as e:
                print(f"Error al acceder a {url}: {e}")
                traceback.print_exc()

    def close(self):
        self.driver.quit()
        self.temp_user_data_dir.cleanup()


# Ejemplo de uso:
# crawler = CubaTravelCrawler()
# crawler.crawl(["https://www.cuba.travel/", ...])
# crawler.close()
