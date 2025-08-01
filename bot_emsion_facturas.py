import telebot
import os  # para la búsqueda
from telebot import types
from main import main_hasta_items
from file_operations import (esperar_archivo_por_patron, rename_and_move_file, read_sheet_data, debounced_write)
from invoice_operations2 import (confirm_invoice_emission,add_observations,obtener_importe_total, add_data_guia)
import textwrap

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
    bot.register_next_step_handler(message, process_confirmation)#,ruc) # el error solo era quitar ruc
bot.message_handler(commands=['emitir'])(handle_emitir)

# Confirmación de emisión

def process_confirmation(message):
    chat_id = message.chat.id
    texto = message.text.strip().lower()

    if texto == 'si':
        sessions[chat_id] = sessions.get(chat_id, {})

        # Aquí comienza el flujo de observación
        iniciar_tipo_pago(message)

    else:
        bot.reply_to(message, "❌ Emisión cancelada.")




############################################### Iniciar selección de tipo de pago
def iniciar_tipo_pago(message):
    chat_id = message.chat.id
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("AL CONTADO", callback_data="pago_contado"),
        types.InlineKeyboardButton("TRANSFERENCIA", callback_data="pago_transferencia")
    )
    bot.send_message(chat_id, "¿Cuál es el tipo de pago?", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data in ["pago_contado", "pago_transferencia"])
def capturar_tipo_pago(call):
    chat_id = call.message.chat.id
    sessions[chat_id] = sessions.get(chat_id, {})
    sessions[chat_id]["tipo_pago"] = "AL CONTADO" if call.data == "pago_contado" else "TRANSFERENCIA"
    bot.answer_callback_query(call.id)
    iniciar_captura_guia(call.message)
    print("funcion 3. capturar_tipo_pago")

# Iniciar el flujo de captura de datos de guía
def iniciar_captura_guia(message):
    chat_id = message.chat.id
    sessions[chat_id]["guias"] = []
    bot.send_message(chat_id, "Ingrese la SERIE de la guía (Ej: B001):")
    bot.register_next_step_handler(message, recibir_serie)

def recibir_serie(message):
    chat_id = message.chat.id
    if "guias" not in sessions[chat_id]:
        sessions[chat_id]["guias"] = []
    sessions[chat_id]["guia_temp"] = {"serie": message.text.strip()}
    bot.send_message(chat_id, "Ingrese el NÚMERO de la guía (Ej: 123456):")
    bot.register_next_step_handler(message, recibir_numero)

def recibir_numero(message):
    chat_id = message.chat.id
    if "guia_temp" not in sessions[chat_id]:
        bot.reply_to(message, "❌ Error interno. Reinicie la operación.")
        return
    sessions[chat_id]["guia_temp"]["numero"] = message.text.strip()
    sessions[chat_id]["guias"].append(sessions[chat_id]["guia_temp"])
    sessions[chat_id].pop("guia_temp")

    # Preguntar si desea agregar otra guía
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("➕ Agregar otra guía", callback_data="agregar_otra_guia"),
        types.InlineKeyboardButton("✅ Finalizar guías", callback_data="finalizar_guias")
    )
    bot.send_message(chat_id, "¿Deseas agregar otra guía?", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data in ["agregar_otra_guia", "finalizar_guias"])
def manejar_opciones_guias(call):
    chat_id = call.message.chat.id
    if call.data == "agregar_otra_guia":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "Ingrese la SERIE de la nueva guía:")
        bot.register_next_step_handler_by_chat_id(chat_id, recibir_serie)

    elif call.data == "finalizar_guias":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "¿Deseas emitir la factura ahora? (si / no)")
        bot.register_next_step_handler_by_chat_id(chat_id, confirmar_emision_despues_de_guias)


def confirmar_emision_despues_de_guias(message):
    texto = message.text.strip().lower()
    if texto == "si":
        continuar_emision(message)
    else:
        bot.reply_to(message, "❌ Emisión cancelada.")


# Proceso final que llama a Selenium
def continuar_emision(message):
    chat_id = message.chat.id
    tipo_pago = sessions[chat_id].get("tipo_pago", "AL CONTADO")
    guias = sessions[chat_id].get("guias", [])
    try:
        add_observations(tipo_pago, guias)
        confirm_invoice_emission()
        bot.reply_to(message, "✅ Factura emitida con éxito.")
        name_pdf = rename_and_move_file(download_folder, destination_folder)
        encontrado = esperar_archivo_por_patron(dir_buscar, name_pdf)
        if encontrado:
            ruta = os.path.join(dir_buscar, encontrado)
            with open(ruta, 'rb') as f:
                bot.send_document(chat_id, f)
        else:
            bot.reply_to(message, "❌ PDF no encontrado.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error durante emisión: {e}")


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
def build_table_markdown(items, desc_width=30):  ############# AQUI ESTA EL ANCHO DE DESCRIPCION
    """
    Construye la tabla en ASCII. Envuelve la columna DESCRIPCION
    cada desc_width caracteres para no romper el layout.
    """
    wrapped = []
    for it in items:
        # envuelvo la descripción en varias líneas
        lines = textwrap.wrap(str(it.get("DESCRIPCION","")), width=desc_width)
        # reuno en un solo string con saltos
        it_desc = "\n".join(lines) if lines else ""
        wrapped.append({
            "CANT":        it.get("CANT",""),
            "DESCRIPCION": it_desc,
            "P.UNIT":      it.get("P.UNIT",""),
            "IMPORTE":     it.get("IMPORTE",""),
        })

    tabla = tabulate(
        wrapped,
        headers="keys",
        tablefmt="grid",
        showindex=range(1, len(wrapped)+1)
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
