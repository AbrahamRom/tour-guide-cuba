# Configuración del crawler para cuba.travel basada en robots.txt

CRAWLER_CONFIG = {
    "sitemap": "https://www.cuba.travel/sitemapindex.xml",
    "user_agents": {
        "*": {
            "disallow": [
                "/admin/",
                "/App_Browsers/",
                "/App_Code/",
                "/App_Data/",
                "/App_GlobalResources/",
                "/bin/",
                "/Components/",
                "/Config/",
                "/contest/",
                "/controls/",
                "/dnn-api/",
                "/Documentation/",
                "/HttpModules/",
                "/Install/",
                "/Providers/",
                "/Resources/ContentRotator/",
                "/Resources/ControlPanel/",
                "/Resources/Dashboard/",
                "/Resources/FeedBrowser/",
                "/Resources/OpenForceAd/",
                "/Resources/SkinWidgets/",
                "/Resources/TabStrip/",
                "/Resources/Widgets/",
                "/Activity-Feed/userId/",
                "/activity-feed/",
                "/users/",
                "/docs/",
                "/DesktopModules/LinkExchange/",
                "/wiki/Page/DotNetNuke-Cookie-usage",
                "/community?utm_term*",
                "/community?utm_source*",
                "/*/ctl/",
                "/*?returnurl=",
                "/*postid",
                "*BannerId=**",
                "*VendorId=*",
                "*PortalId=*",
                "*bit.ly=*",
                "*aspxerrorpath=*",
                "*cx=*",
                "*fileticket=*",
                "*tabid=*",
                "*forumid=*",
                "*mid=*",
                "*groupId=*",
                "*GroupID=*",
                "*helpversion=*",
                "*link=*",
                "*name=*",
                "*page=*",
                "*path=*",
                "*project=*",
                "*scope=*",
                "*skinningcontest=*",
                "*TabID=*",
                "*ModuleID=*",
                "*AuthorID=*",
                "*tag=*",
                "*tags=*",
                "*td=*",
                "*time=*",
            ],
            "crawl_delay": None,
        },
        "msnbot": {
            "disallow": "*",  # Igual que el user-agent general
            "crawl_delay": 2,
        },
        "Slurp": {"disallow": "*", "crawl_delay": 5},  # Igual que el user-agent general
        "Googlebot": {
            "disallow": "*",  # Igual que el user-agent general
            "crawl_delay": None,
        },
        "Owlin Bot v. 3.0": {"disallow": ["/"], "crawl_delay": None},
        "Owlin Bot": {"disallow": ["/"], "crawl_delay": None},
        "Owlin": {"disallow": ["/"], "crawl_delay": None},
    },
}

# Parámetros de configuración para Selenium
SELENIUM_CONFIG = {
    "driver": "chrome",  # Puede ser 'chrome', 'firefox', etc.
    "headless": False,  # Cambia a True si deseas ejecutar en modo headless
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (compatible; TourGuideCubaBot/1.0; +https://www.cuba.travel)",
    "implicit_wait": 10,  # segundos
    "page_load_timeout": 120,  # segundos
    "download_dir": None,  # Puedes especificar un directorio de descargas si lo necesitas
    "disable_images": False,  # Si deseas deshabilitar la carga de imágenes
    "disable_javascript": False,  # Si deseas deshabilitar JavaScript
    "disable_notifications": False,  # Si deseas deshabilitar notificaciones
    "disable_cookies": False,  # Si deseas deshabilitar cookies
    "disable_stylesheets": False,  # Si deseas deshabilitar hojas de estilo
}

# Puedes acceder a la configuración de Selenium desde este archivo importando SELENIUM_CONFIG
