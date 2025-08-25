from bot_emision_facturas import bot
from services.sheet_google.funciones_hoja_google import flush_items_to_sheet
from services.selenium.invoice_logic import login_to_system, navigate_to_invoice_section, input_client_data, create_invoice, confirm_invoice_emission, obtener_importe_total, add_observations
from utils.file_operations import read_sheet_data

# ESTA FALTANDO COMO DEPURAR !
def send_welcome(message):
    comandos = (
        "👋 ¡Bienvenido! Aquí están los comandos disponibles:\n"
        "1️⃣ /mostrar - Mostrar datos de Google Sheets.\n"
        "2️⃣ /items   - Mostrar y editar ítems en línea.\n"
        "3️⃣ /emitir  - Emitir factura.\n"
    )
    bot.reply_to(message, comandos)

def handle_emitir(message):
    partes = message.text.split()
    if len(partes) != 2 or not partes[1].isdigit() or len(partes[1]) != 11:
        return bot.reply_to(message, "❌ Usa /emitir <RUC> con 11 dígitos.")
    ruc_cliente = partes[1] # se almacena el ruc del cliente

    # 1
    flush_items_to_sheet(message.chat.id) # cargamos la tabla al sheets
    bot.reply_to(message, f"⚙️ Iniciando emisión factura RUC {ruc}...")
    # 2
    items = read_sheet_data("fracturas")  # extraemos el ruc y el diccionario, para usarlos en el login
    # 3
    login_to_system()
    # 4
    input_client_data(ruc_cliente) # ruc del cliente
    # 5
    navigate_to_invoice_section()
    # 6
    create_invoice(items)

def register_commands(bot):
    bot.message_handler(commands=['start'])(send_welcome)
    bot.message_handler(commands=['emitir'])(handle_emitir)
