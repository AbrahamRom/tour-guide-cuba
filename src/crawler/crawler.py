from .crawler_config import CRAWLER_CONFIG, SELENIUM_CONFIG
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import re
import chromedriver_autoinstaller
import tempfile


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
        # Añadir preferencias desde selenium_config
        prefs = self.selenium_config.get("prefs", {})
        if self.selenium_config["download_dir"]:
            prefs["download.default_directory"] = self.selenium_config["download_dir"]
        if prefs:
            options.add_experimental_option("prefs", prefs)

        # service = Service(
        #     "C:\\Descargas\\Utils\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
        # )
        # driver = webdriver.Chrome(service=service, options=options)
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            # Si falla, intenta instalar chromedriver-autoinstaller y reintenta
            chromedriver_autoinstaller.install()
            driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(self.selenium_config["implicit_wait"])
        driver.set_page_load_timeout(self.selenium_config["page_load_timeout"])
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

    def crawl(self, urls):
        for url in urls:
            if not self.is_allowed(url):
                print(f"Saltando (disallow): {url}")
                continue
            try:
                self.driver.get(url)
                print(f"Crawleando: {url}")
                # Aquí puedes extraer datos con Selenium
                time.sleep(self.crawl_delay)
            except Exception as e:
                print(f"Error al acceder a {url}: {e}")

    def close(self):
        self.driver.quit()
        self.temp_user_data_dir.cleanup()


# Ejemplo de uso:
# crawler = CubaTravelCrawler()
# crawler.crawl(["https://www.cuba.travel/", ...])
# crawler.close()
