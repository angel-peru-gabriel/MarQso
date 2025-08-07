import telebot
import os  # para la búsqueda
from telebot import types
from main import main_hasta_items
from file_operations import (esperar_archivo_por_patron, rename_and_move_file, read_sheet_data, debounced_write)
from invoice_operations2 import (confirm_invoice_emission,add_observations,obtener_importe_total, add_data_guia)
import textwrap

from tabulate import tabulate  # Para un formato de tabla más legible


import whisper
# import whisper_bot.src.utils.get_whisper_models
# from whisper_bot.src.utils.reencode_to_target_size import ogg_to_wav_bytes





# Configuración del bot
token = '8055516526:AAGNJ_tRmL5lGVhwBEhnCXunJGWvE8vdTtU'
bot = telebot.TeleBot(token)

# Sesiones por chat_id
sessions = {}

# Rutas y carpetas
dir_buscar = r"C:\Users\Aquino\Documents\ademas\FAC\automatico"
download_folder = r"C:\Users\Aquino\Downloads"
destination_folder = r"C:\Users\Aquino\Documents\ademas\FAC\automatico"

@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    # 1️⃣ Descargar el archivo de audio de Telegram:
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    audio_path = "voz_recibida.ogg"
    with open(audio_path, "wb") as f:
        f.write(downloaded_file)
    print("🎧 Mensaje de voz descargado:", audio_path)

    # 2️⃣ Transcribir usando Whisper (modelo local):

    model = whisper.load_model("small")  # Puedes usar "base", "small", "medium", "large" o el modelo configurado
    result = model.transcribe(audio_path, language='es')  # 'language' en 'auto' detecta automáticamente, aquí forzamos español
    transcripcion = result.get("text")  # Texto transcrito

    # 3️⃣ Enviar la transcripción de vuelta al usuario:
    bot.reply_to(message, f"📝 Transcripción:\n{transcripcion}")

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


# ————— Comando /emitir —————
@bot.message_handler(commands=['emitir'])
def handle_emitir(message):
    partes = message.text.split()
    if len(partes) != 2 or not partes[1].isdigit() or len(partes[1]) != 11:
        return bot.reply_to(message, "❌ Usa /emitir <RUC> con 11 dígitos.")
    ruc = partes[1]
    bot.reply_to(message, f"⚙️ Iniciando emisión factura RUC {ruc}...")
    main_hasta_items(ruc)
    monto = obtener_importe_total()
    bot.reply_to(message, f"El monto es: {monto}")
    bot.reply_to(message, "¿Confirmas emisión? Responde 'si' o 'no'.")
    bot.register_next_step_handler(message, process_confirmation)


def process_confirmation(message):
    chat_id = message.chat.id
    if message.text.strip().lower() != 'si':
        return bot.reply_to(message, "❌ Emisión cancelada.")
    # guardamos sesión
    sessions[chat_id] = {}
    # ahora pedimos tipo de pago
    iniciar_tipo_pago(message)

# ES LO MISMO QUE "process_confirmation" realmente
def confirmar_emision_after_guias(message):
    chat_id = message.chat.id
    if message.text.strip().lower() == 'si':
        continuar_emision(message)
    else:
        bot.reply_to(message, "❌ Emisión cancelada.")

# ————— Paso 1: elegir tipo de pago —————
def iniciar_tipo_pago(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("AL CONTADO", callback_data="pago_contado"),
        types.InlineKeyboardButton("TRANSFERENCIA", callback_data="pago_transferencia")
    )
    bot.send_message(message.chat.id, "¿Cuál es el tipo de pago?", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data in ["pago_contado", "pago_transferencia"])
def capturar_tipo_pago(call):
    chat_id = call.message.chat.id
    # guardamos tipo de pago
    sessions[chat_id]["tipo_pago"] = (
        "AL CONTADO" if call.data == "pago_contado" else "TRANSFERENCIA"
    )
    bot.answer_callback_query(call.id)
    # pasamos al siguiente paso: decidir si agregar guías
    bot.send_message(chat_id, "¿Deseas agregar guías? Responde 'si' o 'no'.")
    bot.register_next_step_handler_by_chat_id(chat_id, decidir_guias)


# ————— Paso 2: decidir si agregar guías —————
def decidir_guias(message):
    chat_id = message.chat.id
    if message.text.strip().lower() == 'si':
        # inicializamos lista de guías
        sessions[chat_id]["guias"] = []
        bot.send_message(chat_id, "Ingrese la SERIE de la guía (Ej: B001):")
        bot.register_next_step_handler_by_chat_id(chat_id, recibir_serie)
    else:
        ###########################################33
        tipo_pago = sessions[chat_id].get("tipo_pago")
        guias = sessions[chat_id].get("guias", [ ])
        add_observations(tipo_pago, guias) # LLEGAMOS HASTA AQUI LA PAGINA u.u
        ##############################################33
        # 👉 Aquí preguntamos antes de emitir
        bot.send_message(chat_id, "¿Confirmas emisión? Responde 'si' o 'no'.")
        bot.register_next_step_handler_by_chat_id(chat_id, confirmar_emision_after_guias)
        # si no quiere guías, vamos directo a emisión
        #continuar_emision(message)


# ————— Paso 3: capturar guías —————
def recibir_serie(message):
    chat_id = message.chat.id
    sessions[chat_id]["guia_temp"] = {"serie": message.text.strip()}
    bot.send_message(chat_id, "Ingrese el NÚMERO de la guía (Ej: 123456):")
    bot.register_next_step_handler_by_chat_id(chat_id, recibir_numero)


def recibir_numero(message):
    chat_id = message.chat.id
    temp = sessions[chat_id].get("guia_temp")
    if not temp:
        return bot.reply_to(message, "❌ Error interno. Reinicia con /emitir.")
    temp["numero"] = message.text.strip()
    sessions[chat_id].setdefault("guias", []).append(temp)
    del sessions[chat_id]["guia_temp"]

    # preguntar si añade otra guía
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("➕ Agregar otra", callback_data="nueva_guia"),
        types.InlineKeyboardButton("✅ Terminar guías", callback_data="fin_guias")
    )
    bot.send_message(chat_id, "¿Otra guía o terminamos?", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data in ["nueva_guia", "fin_guias"])
def manejar_guias(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    if call.data == "nueva_guia":
        bot.send_message(chat_id, "Ingrese la SERIE de la siguiente guía:")
        bot.register_next_step_handler_by_chat_id(chat_id, recibir_serie)
    else:
        ###########################################33
        tipo_pago = sessions[chat_id].get("tipo_pago")
        guias = sessions[chat_id].get("guias", [])
        add_observations(tipo_pago, guias) # LLEGAMOS HASTA AQUI LA PAGINA u.u
        ##############################################33
        # 👉 Preguntamos antes de emitir
        bot.send_message(chat_id, "¿Confirmas emisión? Responde 'si' o 'no'.")
        bot.register_next_step_handler_by_chat_id(chat_id, confirmar_emision_after_guias)



# ————— Paso 4: emitir finalmente —————
def continuar_emision(message):
    chat_id = message.chat.id
    tipo_pago = sessions[chat_id].get("tipo_pago")
    guias     = sessions[chat_id].get("guias", [])
    try:
        # PARA MI Q SE ESTA FALTANDO AQUI
        #add_observations(tipo_pago, guias)
        # una mejor opcion es aqui llamar a una funcion para mostrar un resumen
        # avanzar hasta la ultima pagina, y preguntar por la confirmacion con un if, usnado botones
        # pero la clave es hacer una funcion, para no repetir add_observations arriba
        confirm_invoice_emission() ### AQUI NUEVAMENTE DEBERIA PREGUNTA para ver si esta bien las guias! e incluso modifcarlas

        bot.reply_to(message, "✅ Factura emitida con éxito.")
        name_pdf = rename_and_move_file(download_folder, destination_folder)
        found = esperar_archivo_por_patron(dir_buscar, name_pdf)
        if found:
            with open(os.path.join(dir_buscar, found), 'rb') as f:
                bot.send_document(chat_id, f)
        else:
            bot.reply_to(message, "❌ PDF no encontrado.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error durante emisión: {e}")



# Construcción de tabla Markdown
# Límites máximos por columna
COL_LIMITS = {
    "CANT": 2,          # hasta 99
    "DESCRIPCION": 20,
    "P.UNIT": 4,
    "IMPORTE": 6,
}

HEADERS_ALIAS = {
    "CANT": "C",
    "DESCRIPCION": "DESCRIPCIÓN",
    "P.UNIT": "P.U",
    "IMPORTE": "IMP",
}

def build_table_markdown(items,
                          col_limits=None,
                          headers_alias=None):
    col_limits   = col_limits   or COL_LIMITS
    headers_alias = headers_alias or HEADERS_ALIAS

    # 1) largo más grande por columna (incluye encabezados abreviados)
    max_len = {c: len(headers_alias.get(c, c))
               for c in col_limits}
    for row in items:
        for c in col_limits:
            max_len[c] = max(max_len[c], len(str(row.get(c, ""))))

    # 2) ancho final = min(real, límite)
    widths = {c: min(max_len[c], col_limits[c])
              for c in col_limits}

    # 3) formateo de celdas
    rows_fmt = []
    for r in items:
        row_fmt = {}
        for col in ("CANT", "DESCRIPCION", "P.UNIT", "IMPORTE"):
            txt = str(r.get(col, ""))

            if col == "DESCRIPCION":
                txt = "\n".join(textwrap.wrap(txt, width=widths[col]))
            elif col in ("P.UNIT", "IMPORTE"):        # números → derecha
                txt = txt.rjust(widths[col])
            else:                                     # CANT → texto puro
                txt = txt.ljust(widths[col])

            row_fmt[col] = txt
        rows_fmt.append(row_fmt)

    # 4) tabla sin padding lateral
    tabla = tabulate(
        rows_fmt,
        headers=headers_alias,
        tablefmt="grid",
        showindex=False,
        maxcolwidths=[widths["CANT"], widths["DESCRIPCION"],
                      widths["P.UNIT"], widths["IMPORTE"]],
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
    new_kb = build_edit_keyboard(items)
    new_md = build_table_markdown(items)
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

if __name__ == '__main__':
    print("Iniciando bot emisón facturas...")
    bot.polling(none_stop=True)
