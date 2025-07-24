from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from browser_automation import setup_browser
import time

# Asegurarse de que el navegador esté configurado
driver = setup_browser()

asdasd
def login_to_system():
    print("1. Introducción de credenciales")
    try:
        print("     Iniciando...")
        driver.get("https://dle.rae.es/angel?m=form")  # Reemplaza con la URL correcta  # URL completa

        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "w"))
        )
    except Exception as e:
        print(f"Error al iniciar sesión: {e}")
        raise