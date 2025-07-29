import pandas as pd
import os
import time
import fnmatch
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2.service_account import Credentials
import browser_automation

# importamos sólo para la primera autenticación
from API_authenticate import authenticate_google_sheets

download_folder = r"C:\Users\Aquino\Downloads"

# Autenticación global de Google Sheets (se hace UNA vez al importar)
_GS_CLIENT = authenticate_google_sheets('credentials.json')


def get_sheet(sheet_name: str = 'fracturas'):
    """
    Abre y devuelve la primera pestaña de la hoja indicada.
    """
    try:
        return _GS_CLIENT.open(sheet_name).sheet1
    except Exception as e:
        print(f"[get_sheet] Error al abrir hoja '{sheet_name}': {e}")
        raise


def read_sheet_data(sheet_name: str = 'fracturas'):
    """
    Lee todos los registros de GSheet y devuelve una lista de dicts.
    :param sheet_name: Nombre de la hoja en Google Sheets.
    """
    sheet = get_sheet(sheet_name)
    try:
        records = sheet.get_all_records()
        print(f"[read_sheet_data] {len(records)} filas cargadas desde '{sheet_name}'.")
        return records
    except Exception as e:
        print(f"[read_sheet_data] Error: {e}")
        return []


def write_sheet_data(items, sheet_name: str = 'fracturas'):
    """
    Recibe list[dict] con las claves 'CANT', 'DESCRIPCION', 'P.UNIT', 'IMPORTE'
    y vuelca TODO en bloque a la hoja (sobreescribe A2:Dn).
    :param items: Lista de diccionarios a escribir.
    :param sheet_name: Nombre de la hoja en Google Sheets.
    """
    sheet = get_sheet(sheet_name)
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


def read_csv_data(csv_path): # lectura del archivo csv y conversion a un DICCIONARIO

    df = pd.read_csv(csv_path)
    items = df.to_dict(orient='records') # el diccionario se llama ITEMS

    #print(f"RUC del cliente: {ruc_cliente}")
    print(f"Items cargados: {items}")
    return items

def rename_and_move_file(download_folder, destination_folder): # renombrar el pdf
    print ("renombrando ...")
    # el drive etsta de forma global, solo hay q llamarlo por su funcion del objeto brow_automation
    driver = browser_automation.driver
    if not driver:
        raise RuntimeError("Llama a setup_browser() primero en main.py")

    # aqui necesitas el objeto "driver" necesitas llamarlo creando una variable con ese nombre
    numero_factura_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "numeroComprobante")))
    numero_factura = numero_factura_element.text.strip().replace(" ", "")
    nombre_empresa_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dijit_form_SimpleTextarea_1")))
    nombre_empresa = nombre_empresa_element.get_attribute("value").rstrip()

    ruc_emisor = "20602813712"  # osea por las puras xd
    patron_archivo = f"PDF-DOC-{numero_factura}{ruc_emisor}.pdf" # PATRON
    print(patron_archivo)


    archivo_encontrado = esperar_archivo_Abuscar(download_folder, patron_archivo)
    if archivo_encontrado:
        nuevo_nombre = f"{numero_factura} {nombre_empresa}.pdf"
        os.makedirs(destination_folder, exist_ok=True)
        os.rename(os.path.join(download_folder, archivo_encontrado), os.path.join(destination_folder, nuevo_nombre))
        print(f"Archivo renombrado a: {nuevo_nombre}")

        return nuevo_nombre
    else:
        print(f"No se encontró archivo con el patrón: {patron_archivo}")



# el 3er parametro no lo declaras cuando lo llamas, xq ya esta definido, cuando defines la funcion esperar
def esperar_archivo_Abuscar(carpeta, patron, tiempo_max_espera=30): # esperar a q se descargue para recien buscar el patron
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < tiempo_max_espera:
        archivo = buscar_archivo_por_patron(carpeta, patron) # aqui llama la funcion BUSCAR
        if archivo:
            ################
            return archivo # SI DEVUELVE EL ARCHIVO ENCONTRADO
            ################
        time.sleep(1)
    return None

def buscar_archivo_por_patron(carpeta, patron): # buscar el patron
    archivos = os.listdir(carpeta)
    for archivo in archivos:
        if fnmatch.fnmatch(archivo, patron):
            return archivo
    return None
