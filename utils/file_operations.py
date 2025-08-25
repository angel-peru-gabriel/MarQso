import os
import time
import fnmatch
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from services.selenium import browser_automation

def rename_and_move_file(download_folder, destination_folder):
    """
    Renombra y mueve el PDF descargado usando el driver de Selenium.
    """
    driver = browser_automation.driver
    if driver is None:
        raise RuntimeError("Driver de Selenium no inicializado. Llama a setup_browser() primero.")

    # Esperar y extraer datos de la factura
    numero_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "numeroComprobante"))
    )
    numero = numero_elem.text.strip().replace(" ", "")
    empresa_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dijit_form_SimpleTextarea_1"))
    )
    nombre_emp = empresa_elem.get_attribute("value").rstrip()

    # Construir patrón y buscar archivo
    ruc_emisor = "20602813712"
    patron = f"PDF-DOC-{numero}{ruc_emisor}.pdf"
    print(f"[rename_and_move_file] Buscando patrón: {patron}")
    encontrado = esperar_archivo_por_patron(download_folder, patron, timeout=30)

    if encontrado:
        nuevo = f"{numero} {nombre_emp}.pdf"
        os.makedirs(destination_folder, exist_ok=True)
        os.rename(os.path.join(download_folder, encontrado), os.path.join(destination_folder, nuevo))
        print(f"[rename_and_move_file] Renombrado a: {nuevo}")
        return nuevo
    else:
        print(f"[rename_and_move_file] No se encontró archivo con patrón: {patron}")
        return None

def esperar_archivo_por_patron(carpeta, patron, timeout=30):
    """
    Espera hasta que un archivo aparezca según patron.
    """
    inicio = time.time()
    while time.time() - inicio < timeout:
        for f in os.listdir(carpeta):
            if fnmatch.fnmatch(f, patron):
                return f
        time.sleep(1)
    return None