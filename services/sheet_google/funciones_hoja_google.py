import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_APPLICATION_CREDENTIALS # importa de .env la ruta para acceder a la credencial
from API_authenticate import authenticate_google_sheets
from utils.utils import Debouncer, RateLimiter, retry_with_backoff


_GS_CLIENT = authenticate_google_sheets()# Autenticación global de Google Sheets (se hace UNA vez al importar)
SCOPES = [ # Configuración de Google Sheets API
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


# Rate limiter para no superar las 100 llamadas / 100s de Sheets
_rate_limiter = RateLimiter(max_calls=100, period=100)
@retry_with_backoff(max_attempts=5, exceptions=(Exception,))
def write_sheet_data(items, sheet_name: str = 'fracturas'):
    """
    Recibe list[dict] con las claves 'CANT', 'DESCRIPCION', 'P.UNIT', 'IMPORTE'
    y vuelca TODO en bloque a la hoja (sobreescribe A2:Dn).
    Aplica rate limiting y reintentos con back-off.
    """
    if not _rate_limiter.allow():
        raise RuntimeError("Rate limit exceeded for Google Sheets API")
    sheet = _GS_CLIENT.open(sheet_name).sheet1
    values = [
        [itm.get('CANT',''),
         itm.get('DESCRIPCION',''),
         itm.get('P.UNIT',''),
         itm.get('IMPORTE','')]
        for itm in items
    ]
    end_row = len(values) + 1
    try:
        sheet.update(f"A2:D{end_row}", values)
        print(f"[write_sheet_data] {len(values)} filas escritas en hoja '{sheet_name}'.")
    except Exception as e:
        print(f"[write_sheet_data] Error: {e}")
        raise

debounced_write = Debouncer(write_sheet_data, wait=30.0)


def read_sheet_data(sheet_name: str = 'fracturas'):
    """
    Lee todos los registros de GSheet y devuelve una lista de dicts.
    """
    try:
        sheet = _GS_CLIENT.open(sheet_name).sheet1
        records = sheet.get_all_records()
        print(f"[read_sheet_data] {len(records)} filas cargadas desde '{sheet_name}'.")
        return records
    except Exception as e:
        print(f"[read_sheet_data] Error: {e}")
        return []


def flush_items_to_sheet(chat_id: int, wait_fallback: float = 1.0):
    """
    Fuerza que los cambios pendientes se suban a Sheets antes de emitir.
    Solo actúa si hubo ediciones en esta sesión.
    """
    sess = sessions.get(chat_id, {})
    if not sess.get('dirty'):
        return  # nada que forzar

    items = sess.get('items')
    if not items:
        return

    try:
        # Si tu Debouncer expone flush(), úsalo
        if hasattr(debounced_write, 'flush'):
            # Algunas implementaciones aceptan items, otras no.
            try:
                debounced_write.flush(items)
            except TypeError:
                debounced_write.flush()
        else:
            # Best-effort: agenda y espera un instante
            debounced_write.call(items)
            time.sleep(wait_fallback)
    finally:
        sess['dirty'] = False
