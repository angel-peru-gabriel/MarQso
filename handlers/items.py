import time
from bot_emision_facturas import bot
from handlers.sessions import get_session, set_session
from services.sheet_google.funciones_hoja_google import read_sheet_data, write_sheet_data
from ui.keyboards import build_table_markdown, build_edit_keyboard, parse_item_line, _mark_dirty, _finish_add_row
from telebot import types
from services.sheet_google.funciones_hoja_google import debounced_write

def show_items(message):
    """
    Muestra los ítems en una tabla con opciones de edición en tiempo real.
    """
    chat_id = message.chat.id
    items = read_sheet_data('fracturas')

    if not items:
        bot.reply_to(message, "❌ No hay ítems aún.")
        return

    # Construir la tabla y el teclado
    text = build_table_markdown(items)
    kb = build_edit_keyboard(items)

    # Enviar el mensaje con la tabla y el teclado
    sent = bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

    # Guardar el ID del mensaje en la sesión para futuras ediciones
    set_session(chat_id, 'items', items)
    set_session(chat_id, 'message_id', sent.message_id)
    set_session(chat_id, 'dirty', False)

def manejar_callback(call):
    """
    Maneja los callbacks del teclado inline para editar, agregar o eliminar filas.
    """
    chat_id = call.message.chat.id
    data = call.data
    session = get_session(chat_id)
    items = session.get("items", [])

    if data.startswith("edit:"):
        indice_fila = int(data.split(":")[1])
        bot.send_message(chat_id, f"✏️ Ingresa los nuevos valores para la fila {indice_fila + 1} en el formato:\nCANTIDAD, DESCRIPCIÓN, P.UNIT")
        set_session(chat_id, 'await_edit_row', indice_fila)

    elif data == "addrow":
        bot.send_message(chat_id, "➕ Ingresa los valores para la nueva fila en el formato:\nCANTIDAD, DESCRIPCIÓN, P.UNIT")
        set_session(chat_id, 'await_new_row', True)

    elif data.startswith("delete:"):
        indice_fila = int(data.split(":")[1])
        items.pop(indice_fila)
        _mark_dirty(chat_id, session)
        actualizar_tabla_items(chat_id)

def recibir_texto_nueva_fila(mensaje):
    """
    Recibe el texto para agregar una nueva fila.
    """
    chat_id = mensaje.chat.id
    session = get_session(chat_id)
    if not session.get("await_new_row"):
        return

    item, error = parse_item_line(mensaje.text)
    if error:
        bot.reply_to(mensaje, f"❌ {error}")
        return

    _finish_add_row(chat_id, item, bot, session, debounced_write=write_sheet_data)

def recibir_texto_editar_fila(mensaje):
    """
    Recibe el texto para editar una fila existente.
    """
    chat_id = mensaje.chat.id
    session = get_session(chat_id)
    indice_fila = session.get("await_edit_row")
    if indice_fila is None:
        return

    item, error = parse_item_line(mensaje.text)
    if error:
        bot.reply_to(mensaje, f"❌ {error}")
        return

    session["items"][indice_fila] = item
    _mark_dirty(chat_id, session)
    actualizar_tabla_items(chat_id)

    session.pop("await_edit_row", None)

def actualizar_tabla_items(chat_id):
    """
    Actualiza la tabla de ítems en el mensaje del chat.
    """
    session = get_session(chat_id)
    items = session.get("items", [])
    nuevo_md = build_table_markdown(items)
    nuevo_teclado = build_edit_keyboard(items)
    bot.edit_message_text(nuevo_md, chat_id, session["message_id"],
                          parse_mode="Markdown", reply_markup=nuevo_teclado)

def flush_items_to_sheet(chat_id: int, wait_fallback: float = 1.0):
    session = get_session(chat_id)
    if not session.get('dirty'):
        return

    items = session.get('items')
    if not items:
        return

    try:
        if hasattr(debounced_write, 'flush'):
            try:
                debounced_write.flush(items)
            except TypeError:
                debounced_write.flush()
        else:
            debounced_write.call(items)
            time.sleep(wait_fallback)
    finally:
        session['dirty'] = False


# esto lo inicializa en bot_emision_facturas.py
def register_items_handlers(bot):
    """
    Registra los manejadores relacionados con los ítems.
    """
    bot.message_handler(commands=['items'])(show_items)
    bot.callback_query_handler(func=lambda call: call.data.startswith(("edit:", "addrow", "delete:")))(manejar_callback)
    bot.message_handler(func=lambda msg: get_session(msg.chat.id).get("await_new_row"))(recibir_texto_nueva_fila)
    bot.message_handler(func=lambda msg: get_session(msg.chat.id).get("await_edit_row") is not None)(recibir_texto_editar_fila)