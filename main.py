from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from file_operations import read_csv_data, rename_and_move_file, read_sheet_data
import time
from browser_automation import setup_browser, close_browser#, init_driver
from invoice_operations2 import login_to_system, navigate_to_invoice_section, input_client_data, create_invoice, confirm_invoice_emission, obtener_importe_total, add_observations

download_folder = r"C:\Users\Aquino\Downloads"
destination_folder = r"C:\Users\Aquino\Documents\ademas\FAC\automatico"
#ruc_cliente = 20605841318

def main_hasta_items(ruc_cliente):  # esto es lo que vas a importar
    #driver = None
    try:

        # Leer datos del archivo CSV
        csv_path = r"C:\Users\Aquino\PycharmProjects\AQUINO_SELENIUM\facturas.csv"

        items = read_sheet_data("fracturas") # extraemos el ruc y el diccionario, para usarlos en el login
        #ruc_cliente = 20603721692

        # Inicializo driver + carpeta de descargas
        setup_browser(download_folder)

        # Iniciar sesión y navegar al sistema de facturación
        login_to_system()
        # 1. LOGEARSE
        # nos logeamos con nuestro ruc, el parametro es introducido en otra operacion

        # Navegar a la sección de facturas, 2. NAVEGACION
        navigate_to_invoice_section()

        # Ingresar datos del cliente, 3. DATOS CLIENTE
        input_client_data(ruc_cliente)

        # Crear la factura, 4. AGREGAS ITEMS
        create_invoice(items)

        # Agregar comentarios
        #add_observations("AL CONTADO")

        print("El proceso terminó correctamente.")   # Confirmación explícita de éxito
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        raise # CONVIENE Q LOS PROCESO ESTE EN EL MAIN para depurarlos

    finally: # ESTO HACE QUE TODO SE CORTE!!!
        # esto siempre se ejecutara, para cerrar el cidog
        # Cerrar el navegador
        print("🔧 Cerrando el navegador...")
        #close_browser()


if __name__ == "__main__":
    main_hasta_items()
