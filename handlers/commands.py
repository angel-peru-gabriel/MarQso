from bot_emision_facturas import bot
from services.sheet_google.funciones_hoja_google import flush_items_to_sheet
from services.selenium.invoice_logic import login_to_system, navigate_to_invoice_section, input_client_data, create_invoice
# from utils.file_operations import read_sheet_data
# from guias import ask_for_guias, confirm_billing

def send_welcome(message):
    comandos = (
        "👋 ¡Bienvenido! Aquí están los comandos disponibles:\n"
        "1️⃣ /mostrar - Mostrar datos de Google Sheets.\n"
        "2️⃣ /items   - Mostrar y editar ítems en línea.\n"
        "3️⃣ /emitir  - Emitir factura.\n"
    )
    bot.reply_to(message, comandos)


def handle_emitir(message):
    """
    El comando /emitir, que procesa el RUC, lee los ítems desde Google Sheets,
    y luego llama a las funciones de Selenium para emitir la factura.
    """
    partes = message.text.split()
    if len(partes) != 2 or not partes[1].isdigit() or len(partes[1]) != 11:
        return bot.reply_to(message, "❌ Usa /emitir <RUC> con 11 dígitos.")

    ruc_cliente = partes[1]  # se almacena el RUC del cliente

    # 1) Actualizamos los ítems en Google Sheets
    flush_items_to_sheet(message.chat.id)
    bot.reply_to(message, f"⚙️ Iniciando emisión factura RUC {ruc_cliente}...")


#

def register_commands(bot):
    """
    Esta función registra los comandos que el bot podrá manejar.
    - /start: muestra la bienvenida y los comandos disponibles.
    - /emitir: maneja el proceso de emisión de la factura.
    """
    bot.message_handler(commands=['start'])(send_welcome)
    bot.message_handler(commands=['emitir'])(handle_emitir)
