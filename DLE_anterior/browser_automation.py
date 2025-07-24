from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # Import necesario para inicializar el servicio de ChromeDriver (en sistemas como Raspberry Pi).
from selenium.webdriver.chrome.options import Options  # Importa opciones para configurar el navegador Chrome.
import logging  # Para registrar mensajes de información, errores y depuración.
from selenium.webdriver.support.ui import WebDriverWait  # Ayuda a esperar de manera explícita hasta que ciertas condiciones se cumplan.
from selenium.webdriver.support import expected_conditions as EC  # Define condiciones como la visibilidad o presencia de elementos.
from selenium.webdriver.common.by import By  # Permite localizar elementos en el DOM mediante selectores como ID, CLASS_NAME, etc.

# ANGEL
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# Configuración básica de logging para mostrar mensajes de información, advertencias y errores.
# Los mensajes seguirán un formato estándar con la hora, el nivel del log (INFO, ERROR, etc.) y el mensaje.

# Variable global para el navegador
driver = None  # Declaración de una variable global para almacenar la instancia del navegador.


def setup_browser1():
    """
    Configura y abre el navegador Chrome en modo headless (sin interfaz gráfica),
    con ajustes para evitar ser detectado como un bot.

    Retorna:
        driver: Una instancia configurada del navegador Chrome.
    """
    global driver  # Se usa la variable global para permitir su reutilización en todo el proyecto.
    if driver is None:  # Solo se configura si el navegador no está ya inicializado.
        try:
            logging.info(
                "Configurando navegador...")  # Mensaje de log para indicar que se está configurando el navegador.
            options = Options()  # Crea un objeto para configurar las opciones del navegador.

            # Modo headless (sin interfaz gráfica)
            options.add_argument('--headless')  # Permite ejecutar el navegador sin abrir una ventana gráfica.
            options.add_argument('--no-sandbox')  # Deshabilita el aislamiento del proceso, útil en entornos limitados.
            options.add_argument('--disable-dev-shm-usage')  # Usa memoria compartida de manera más eficiente.
            options.add_argument('--disable-gpu')  # Deshabilita la aceleración por GPU, mejora la compatibilidad.
            options.add_argument('--window-size=1920,1080')  # Configura el tamaño de la ventana del navegador.

            # Ajustes para evitar detección como bot
            options.add_argument(
                '--disable-blink-features=AutomationControlled')  # Evita que los sitios detecten que es un navegador automatizado.
            options.add_argument(
                '--disable-infobars')  # Deshabilita la barra de información "Chrome is being controlled by automated software".
            options.add_argument('--disable-extensions')  # Deshabilita extensiones en el navegador.
            options.add_argument('--disable-popup-blocking')  # Deshabilita bloqueos de ventanas emergentes.
            options.add_argument('--disable-notifications')  # Desactiva las notificaciones del navegador.
            options.add_argument('--disable-web-security')  # Permite acceder a contenido de dominios cruzados.

            # Cambiar el User-Agent para simular un navegador "normal"
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
            )
            # Cambia el User-Agent para que el navegador automatizado parezca ser un navegador convencional.

            # Inicializar el navegador
            driver = webdriver.Chrome(options=options)  # Crea una instancia de Chrome con las opciones configuradas.
            logging.info(
                "Navegador iniciado correctamente en modo headless.")  # Indica que el navegador se inició sin problemas.

        except Exception as e:
            # Si ocurre algún error al inicializar el navegador, registra el error y vuelve a lanzarlo.
            logging.error(f"Error al iniciar el navegador: {e}")
            raise
    return driver  # Retorna la instancia configurada del navegador.


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


def setup_browser():
    # Configura y abre el navegador Chrome.
    # Asigna la instancia del navegador a la variable global `driver`.
    print("entro")
    global driver
    if driver is None:
        try:
            print("ya")
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

