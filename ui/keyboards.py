from telebot import types
from tabulate import tabulate
import textwrap


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

def build_main_keyboard():
    # Lógica para construir el teclado principal
    pass

# Aqui deberia estar la plantilla de lo botones de confirmacion de si o no
def build_confirmation_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("✅ Sí", callback_data="confirm:yes"),
        types.InlineKeyboardButton("❌ No", callback_data="confirm:no")
    )
    return kb


def build_table_markdown(items, col_limits=None, headers_alias=None):
    col_limits = col_limits or COL_LIMITS
    headers_alias = headers_alias or HEADERS_ALIAS

    max_len = {c: len(headers_alias.get(c, c)) for c in col_limits}
    for row in items:
        for c in col_limits:
            max_len[c] = max(max_len[c], len(str(row.get(c, ""))))

    widths = {c: min(max_len[c], col_limits[c]) for c in col_limits}

    rows_fmt = []
    for r in items:
        row_fmt = {}
        for col in ("CANT", "DESCRIPCION", "P.UNIT", "IMPORTE"):
            txt = str(r.get(col, ""))
            if col == "DESCRIPCION":
                txt = "\n".join(textwrap.wrap(txt, width=widths[col]))
            elif col in ("P.UNIT", "IMPORTE"):
                txt = txt.rjust(widths[col])
            else:
                txt = txt.ljust(widths[col])
            row_fmt[col] = txt
        rows_fmt.append(row_fmt)

    tabla = tabulate(
        rows_fmt,
        headers=headers_alias,
        tablefmt="grid",
        showindex=False,
        maxcolwidths=[widths["CANT"], widths["DESCRIPCION"], widths["P.UNIT"], widths["IMPORTE"]],
    )
    return f"```{tabla}```"

def build_edit_keyboard(items):
    kb = types.InlineKeyboardMarkup(row_width=3)
    botones = [
        types.InlineKeyboardButton(f"✏️ Editar fila {i+1}", callback_data=f"edit:{i}")
        for i in range(len(items))
    ]
    if botones:
        kb.add(*botones)
    kb.add(types.InlineKeyboardButton("➕ Agregar fila", callback_data="addrow"))
    return kb

def parse_item_line(texto: str):
    raw = [p.strip() for p in texto.replace('\n', ' ').split(',')]
    if len(raw) < 3:
        return None, "Formato inválido. Usa: CANTIDAD, DESCRIPCIÓN, P.UNIT"
    cant_s, desc, precio_s = raw[0], ",".join(raw[1:-1]) or raw[1], raw[-1]

    def to_float(s):
        return float(s.replace(',', '.'))

    try:
        cant = to_float(cant_s)
        precio = to_float(precio_s)
    except ValueError:
        return None, "Cantidad y precio deben ser números."

    cant_txt = str(int(cant)) if cant.is_integer() else str(cant)
    punit_txt = f"{precio:.2f}".rstrip('0').rstrip('.')
    importe = cant * precio
    importe_txt = f"{importe:.2f}".rstrip('0').rstrip('.')

    item = {
        "CANT": cant_txt,
        "DESCRIPCION": desc,
        "P.UNIT": punit_txt,
        "IMPORTE": importe_txt,
    }
    return item, None

def _mark_dirty(chat_id: int, sessions: dict):
    sessions.setdefault(chat_id, {})
    sessions[chat_id]['dirty'] = True

def _finish_add_row(chat_id, item, bot, sessions, debounced_write):
    items = sessions.get(chat_id, {}).get('items', [])
    items.append(item)
    debounced_write.call(items)
    _mark_dirty(chat_id, sessions)

    new_md = build_table_markdown(items)
    new_kb = build_edit_keyboard(items)
    bot.edit_message_text(new_md, chat_id, sessions[chat_id]['message_id'],
                          parse_mode="Markdown", reply_markup=new_kb)

    sessions[chat_id].pop('await_new_row', None)
    bot.send_message(chat_id, "✅ Fila agregada.")