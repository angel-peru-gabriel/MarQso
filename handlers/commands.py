from bot_emision_facturas import bot
from services.sheet_google.funciones_hoja_google import flush_items_to_sheet

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
    ruc = partes[1]
    flush_items_to_sheet(message.chat.id) # cargamos la tabla al sheets
    bot.reply_to(message, f"⚙️ Iniciando emisión factura RUC {ruc}...")
    # Continuar emisión, etc.

def register_commands(bot):
    bot.message_handler(commands=['start'])(send_welcome)
    bot.message_handler(commands=['emitir'])(handle_emitir)
