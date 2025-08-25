# Este módulo centraliza el manejo del diccionario de sesiones

_sessions = {}  # Diccionario privado para almacenar las sesiones

# por las puras escribias el condicional siempre, cuando se podia hacer una funcion
def get_session(chat_id):
    """
    Obtiene la sesión de un chat específico. Si no existe, la crea.
    """
    if chat_id not in _sessions:
        _sessions[chat_id] = {}
    return _sessions[chat_id]

def set_session(chat_id, key, value):
    """
    Establece un valor en la sesión de un chat específico.
    """
    session = get_session(chat_id)
    session[key] = value

def delete_session(chat_id):
    """
    Elimina la sesión de un chat específico.
    """
    if chat_id in _sessions:
        del _sessions[chat_id]

def clear_sessions():
    """
    Limpia todas las sesiones.
    """
    _sessions.clear()