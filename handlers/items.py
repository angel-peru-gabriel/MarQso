from bot_emsion_facturas import bot
from services.sheet_google.funciones_hoja_google import read_sheet_data
from ui.keyboards import build_edit_keyboard

def cmd_items(message):
    chat_id = message.chat.id
    items = read_sheet_data('fracturas')
    if not items:
        bot.reply_to(message, "❌ No hay ítems aún.")
        return
    text = build_table_markdown(items)
    kb = build_edit_keyboard(items)
    sent = bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

def register_items_handlers(bot):
    bot.message_handler(commands=['items'])(cmd_items)
