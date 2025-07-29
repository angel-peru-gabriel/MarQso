import telebot
import os  # para la búsqueda
from telebot import types
from main import main_hasta_items
from file_operations import (
    esperar_archivo_por_patron,
    rename_and_move_file,
    read_sheet_data,
    debounced_write
)
from invoice_operations2 import (
    confirm_invoice_emission,
    add_observations,
    obtener_importe_total
)
import pandas as pd
from tabulate import tabulate  # Para un formato de tabla más legible

# Configuración del bot
token = '8055516526:AAGNJ_tRmL5lGVhwBEhnCXunJGWvE8vdTtU'
bot = telebot.TeleBot(token)

# Sesiones por chat_id
sessions = {}

# Rutas y carpetas
dir_buscar = r"C:\Users\Aquino\Documents\ademas\FAC\automatico"
download_folder = r"C:\Users\Aquino\Downloads"
destination_folder = r"C:\Users\Aquino\Documents\ademas\FAC\automatico"

# Comando /start
def send_welcome(message):
    comandos = (
        "👋 ¡Bienvenido! Aquí están los comandos disponibles:\n"
        "1️⃣ /mostrar - Mostrar datos de Google Sheets.\n"
        "2️⃣ /items   - Mostrar y editar ítems en línea.\n"
        "3️⃣ /emitir  - Emitir factura.\n"
    )
    bot.reply_to(message, comandos)
bot.message_handler(commands=['start'])(send_welcome)

# Comando /emitir
def handle_emitir(message):
    partes = message.text.split()
    if len(partes) != 2 or not partes[1].isdigit() or len(partes[1]) != 11:
        bot.reply_to(message, "❌ Usa /emitir <RUC> con 11 dígitos.")
        return
    ruc = partes[1]
    bot.reply_to(message, f"⚙️ Iniciando emisión factura RUC {ruc}...")
    main_hasta_items(ruc)
    monto = obtener_importe_total()
    bot.reply_to(message, f"El monto es: {monto}")
    bot.reply_to(message, "¿Confirmas emisión? Responde 'si' o 'no'.")
    bot.register_next_step_handler(message, process_confirmation, ruc)
bot.message_handler(commands=['emitir'])(handle_emitir)

# Confirmación de emisión
def process_confirmation(message, ruc_cliente):
    texto = message.text.strip().lower()
    if texto == 'si':
        add_observations("AL CONTADO")
        confirm_invoice_emission()
        bot.reply_to(message, "✅ Factura emitida con éxito.")
        name_pdf = rename_and_move_file(download_folder, destination_folder)
        encontrado = esperar_archivo_por_patron(dir_buscar, name_pdf)
        if encontrado:
            ruta = os.path.join(dir_buscar, encontrado)
            with open(ruta, 'rb') as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.reply_to(message, "❌ PDF no encontrado.")
    else:
        bot.reply_to(message, "❌ Emisión cancelada.")
bot.register_next_step_handler_by_chat_id

# Comando /mostrar (Google Sheets)
def mostrar_excel(message):
    records = read_sheet_data('fracturas')
    if not records:
        bot.reply_to(message, "❌ No hay datos en la hoja.")
        return
    texto = tabulate(records, headers="keys", tablefmt="grid", showindex=True)
    for i in range(0, len(texto), 4000):
        bot.reply_to(message, texto[i:i+4000])
bot.message_handler(commands=['mostrar'])(mostrar_excel)

# Construcción de tabla Markdown
def build_table_markdown(items):
    # Si alguna descripción contiene '\n', tabulate la mostrará en múltiples líneas
    tabla = tabulate(
        items,
        headers="keys",
        tablefmt="grid",
        showindex=range(1, len(items) + 1)
    )
    return f"```{tabla}```"

# Teclado inline para editar filas
def build_edit_keyboard(items):
    kb = types.InlineKeyboardMarkup(row_width=3)
    botones = []
    for i in range(len(items)):
        botones.append(
            types.InlineKeyboardButton(
                f"✏️ Editar fila {i+1}", callback_data=f"edit:{i}"
            )
        )
    kb.add(*botones)
    return kb

# Comando /items
@bot.message_handler(commands=['items'])
def cmd_items(message):
    chat_id = message.chat.id
    items = read_sheet_data('fracturas')
    if not items:
        bot.reply_to(message, "❌ No hay ítems aún.")
        return
    text = build_table_markdown(items)
    kb = build_edit_keyboard(items)
    sent = bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)
    sessions[chat_id] = {"message_id": sent.message_id, "items": items}

# Seleccionar fila a editar
@bot.callback_query_handler(lambda c: c.data.startswith('edit:'))
def on_edit_row(call):
    chat_id = call.message.chat.id
    idx = int(call.data.split(':')[1])
    sessions[chat_id]['edit'] = {'row': idx}
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton('Cantidad', callback_data=f'field:{idx}:CANT'),
        types.InlineKeyboardButton('Descripción', callback_data=f'field:{idx}:DESCRIPCION'),
        types.InlineKeyboardButton('Precio Unitario', callback_data=f'field:{idx}:P.UNIT')
    )
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id, f"¿Qué campo fila {idx+1}?", reply_markup=kb)

# Seleccionar campo a editar
@bot.callback_query_handler(lambda c: c.data.startswith('field:'))
def on_field_selected(call):
    chat_id = call.message.chat.id
    _, idx_str, field = call.data.split(':')
    sessions[chat_id]['edit']['field'] = field
    bot.answer_callback_query(call.id)
    bot.send_message(
        chat_id,
        f"Envía el nuevo valor para {field} (fila {int(idx_str)+1}):"
    )
    bot.register_next_step_handler_by_chat_id(chat_id, process_new_value)

# Procesar nuevo valor y redibujar tabla
def process_new_value(message):
    chat_id = message.chat.id
    sess = sessions.get(chat_id)
    if not sess or 'edit' not in sess:
        bot.reply_to(message, '❌ No hay edición en curso.')
        return
    idx = sess['edit']['row']
    field = sess['edit']['field']
    items = sess['items']

    # Actualizar en memoria
    items[idx][field] = message.text

    # Redibujar mensaje con tabla actualizada
    new_md = build_table_markdown(items)
    new_kb = build_edit_keyboard(items)
    bot.edit_message_text(
        new_md,
        message.chat.id,
        sess['message_id'],
        parse_mode="Markdown",
        reply_markup=new_kb
    )

    # Programar guardado en Google Sheets
    debounced_write.call(items)

    bot.reply_to(message, f"✅ Fila {idx+1} {field} actualizada.")
    sess.pop('edit', None)



if __name__ == '__main__':
    print("Iniciando bot emisón facturas...")
    bot.polling(none_stop=True)
