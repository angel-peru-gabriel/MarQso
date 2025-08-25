from telebot import types

def build_main_keyboard():
    # Lógica para construir el teclado principal
    pass

def build_edit_keyboard(items):
    kb = types.InlineKeyboardMarkup(row_width=3)
    botones = []
    for i in range(len(items)):
        botones.append(
            types.InlineKeyboardButton(
                f"✏️ Editar fila {i+1}", callback_data=f"edit:{i}"
            )
        )
    if botones:
        kb.add(*botones)
    # botón global para crear nuevas filas
    kb.add(types.InlineKeyboardButton("➕ Agregar fila", callback_data="addrow"))
    return kb

