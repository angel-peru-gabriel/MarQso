from selenium import webdriver
from selenium.webdriver.chrome.service import Service # falta en rasbery
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# ANGEL
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Variable global para el navegador
driver = None # #yo : como q creas 1ero la variable! para lugar jugar con ella




# ESO MODIFICAREMOS
def setup_browser(download_folder: str = None):
    """
    Configura y abre el navegador Chrome en modo headless (sin interfaz gráfica),
    con ajustes para evitar ser detectado como un bot.
    """
    global driver
    if driver is None:
        try:
            logging.info("Configurando navegador...")
            options = Options()

            # Si me das download_folder, lo uso como carpeta por defecto
            if download_folder:
                prefs = {
                        "download.default_directory": download_folder,
                        "download.prompt_for_download": False,
                        "plugins.always_open_pdf_externally": True
                                                               }
                options.add_experimental_option("prefs", prefs)

            # Modo headless (sin interfaz gráfica)
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')

            # Ajustes para evitar detección como bot
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-web-security')

            # Cambiar el User-Agent para simular un navegador "normal"
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')

            # Inicializar el navegador
            driver = webdriver.Chrome(options=options)
            logging.info("Navegador iniciado correctamente en modo headless.")

        except Exception as e:
            logging.error(f"Error al iniciar el navegador: {e}")
            raise
    return driver

# == Inicialización automática al importar ==
# Al importar este módulo, arranca el navegador una sola vez.
try:
  setup_browser()
except Exception as e:
  logging.error(f"No se pudo iniciar el navegador en import: {e}")


def setup_browser1():
    """
    Configura y abre el navegador Chrome en modo headless (sin interfaz gráfica).
    Asigna la instancia del navegador a la variable global `driver`.
    """
    global driver
    if driver is None:
        try:
            logging.info("Configurando navegador...")
            options = Options()

            # Modo headless (sin interfaz gráfica)
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            # Otras configuraciones
            options.add_argument('--disable-extensions')  # Deshabilitar extensiones
            options.add_argument('--disable-gpu')  # Deshabilitar GPU (recomendado para headless)
            options.add_argument('--window-size=1920,1080')

            # Inicializar el navegador
            driver = webdriver.Chrome(options=options)
            logging.info("Navegador iniciado correctamente en modo headless.")

        except Exception as e:
            logging.error(f"Error al iniciar el navegador: {e}")
            raise
    return driver

def setup_browser2():
    
    #Configura y abre el navegador Chrome.
    #Asigna la instancia del navegador a la variable global `driver`.
    

    global driver
    if driver is None:
        try:
            logging.info("Configurando navegador...")
            options = Options()
            options.add_argument('--start-maximized')  # Maximizar ventana
            options.add_argument('--disable-extensions')  # Deshabilitar extensiones
            options.add_experimental_option("detach", True)  # Mantener navegador abierto
            driver = webdriver.Chrome(options=options)
            logging.info("Navegador iniciado correctamente.")

        except Exception as e:
            logging.error(f"Error al iniciar el navegador: {e}")
            raise
    return driver


def close_browser():
    """
    Cierra el navegador y limpia la variable global `driver`.
    """
    global driver
    if driver is not None:
        try:
            driver.quit()
            logging.info("Navegador cerrado correctamente.")
        except Exception as e:
            logging.error(f"Error al cerrar el navegador: {e}")
        finally:
            driver = None


def cerrar_notificacion():
    try:
        # Verifica si el elemento está presente sin bloquear
        elemento_presente = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "btnCerrar"))
        )
        if elemento_presente:
            # Si el elemento está presente, hacemos clic en "Ver más tarde"
            driver.find_element(By.ID, "btnCerrar").click()
            print("Notificación emergente cerrada.")
    except Exception as e:
        # Si no se encuentra el elemento, no pasa nada
        print("No se encontró la notificación emergente. Continuando con el flujo...")
