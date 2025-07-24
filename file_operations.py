import pandas as pd
import os
import time
import fnmatch
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from API_authenticate import authenticate_google_sheets
from browser_automation import setup_browser
#
import gspread
from google.oauth2.service_account import Credentials

# Asegurarse de que el navegador esté configurado
#download_folder = r"C:\Users\Aquino\Downloads"
driver = setup_browser()

def read_sheet_data(sheet_name, credentials_path='credentials.json'):
    """
    Lee los datos desde una hoja de cálculo de Google Sheets y los convierte en un diccionario.
    Args:
        sheet_name (str): Nombre de la hoja de cálculo a leer.
        credentials_path (str): Ruta al archivo de credenciales JSON.
    Returns:
        list: Lista de diccionarios con los datos de la hoja de cálculo.
    """
    try:
        client = authenticate_google_sheets(credentials_path)
        if client is None:
            raise Exception("Error al autenticar con Google Sheets")

        sheet = client.open(sheet_name).sheet1
        records = sheet.get_all_records()
        print(f"Datos cargados desde Google Sheets: {records}")
        return records
    except Exception as e:
        print(f"Error al leer la hoja de cálculo: {e}")
        return []
def read_csv_data(csv_path): # lectura del archivo csv y conversion a un DICCIONARIO

    df = pd.read_csv(csv_path)
    items = df.to_dict(orient='records') # el diccionario se llama ITEMS

    #print(f"RUC del cliente: {ruc_cliente}")
    print(f"Items cargados: {items}")
    return items

def rename_and_move_file(download_folder, destination_folder): # renombrar el pdf
    print ("renombrando ...")

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
