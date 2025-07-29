import pandas as pd
import os
import time
import fnmatch
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import browser_automation

from API_authenticate import authenticate_google_sheets
from utils import Debouncer, RateLimiter, retry_with_backoff

# Autenticación global de Google Sheets (se hace UNA vez al importar)
_GS_CLIENT = authenticate_google_sheets('credentials.json')

# Rate limiter para no superar las 100 llamadas / 100s de Sheets
_rate_limiter = RateLimiter(max_calls=100, period=100)

@retry_with_backoff(max_attempts=5, exceptions=(Exception,))
def write_sheet_data(items, sheet_name: str = 'fracturas'):
    """
    Recibe list[dict] con las claves 'CANT', 'DESCRIPCION', 'P.UNIT', 'IMPORTE'
    y vuelca TODO en bloque a la hoja (sobreescribe A2:Dn).
    Aplica rate limiting y reintentos con back-off.
    """
    if not _rate_limiter.allow():
        raise RuntimeError("Rate limit exceeded for Google Sheets API")
    sheet = _GS_CLIENT.open(sheet_name).sheet1
    values = [
        [itm.get('CANT',''),
         itm.get('DESCRIPCION',''),
         itm.get('P.UNIT',''),
         itm.get('IMPORTE','')]
        for itm in items
    ]
    end_row = len(values) + 1
    try:
        sheet.update(f"A2:D{end_row}", values)
        print(f"[write_sheet_data] {len(values)} filas escritas en hoja '{sheet_name}'.")
    except Exception as e:
        print(f"[write_sheet_data] Error: {e}")
        raise

# Debouncer para agrupar escrituras tras 30s de inactividad
debounced_write = Debouncer(write_sheet_data, wait=30.0)

def read_sheet_data(sheet_name: str = 'fracturas'):
    """
    Lee todos los registros de GSheet y devuelve una lista de dicts.
    """
    try:
        sheet = _GS_CLIENT.open(sheet_name).sheet1
        records = sheet.get_all_records()
        print(f"[read_sheet_data] {len(records)} filas cargadas desde '{sheet_name}'.")
        return records
    except Exception as e:
        print(f"[read_sheet_data] Error: {e}")
        return []


def read_csv_data(csv_path):
    """
    Lee un CSV y lo convierte a lista de dicts.
    """
    df = pd.read_csv(csv_path)
    items = df.to_dict(orient='records')
    print(f"[read_csv_data] {len(items)} registros cargados desde CSV.")
    return items


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
