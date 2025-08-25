from bot_emision_facturas import bot
from services.selenium.invoice_logic import login_to_system, navigate_to_invoice_section, input_client_data, create_invoice

def start_billing_process(chat_id, ruc_cliente):
   # 2) Leemos los ítems desde la hoja de Google Sheets
   items = read_sheet_data("fracturas")  # extraemos el ruc y el diccionario, para usarlos en el login

   # 3) Iniciar sesión en el sistema de facturación
   login_to_system()

   # 4) Ingresamos los datos del cliente
   input_client_data(ruc_cliente)

   # 5) Navegar a la sección de facturación
   navigate_to_invoice_section()

   # 6) Crear la factura con los ítems leídos
   create_invoice(items)


def confirm_billing(message):
   """
   Maneja la confirmación de emisión de la factura.
   """
   # Preguntar al usuario si desea confirmar la emisión
   # El bot debe dar mostrar dos botones: "Sí" y "No".
   # Para ello llamas a funciones del modulos keyboard.py
   pass

def register_billing_handlers(bot):
   """
   Registra los manejadores relacionados con la facturación.
   """
   # Registrar funciones específicas relacionadas con la facturación
   # Esta funcion es la continaucion, luego de confirmar
   pass


download_folder = r"C:\Users\Aquino\Downloads"
destination_folder = r"C:\Users\Aquino\Documents\ademas\FAC\automatico"
