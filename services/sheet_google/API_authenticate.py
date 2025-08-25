import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_APPLICATION_CREDENTIALS # importa de .env la ruta para acceder a la credencial

# Configuración de Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def authenticate_google_sheets():
    """
    Autentica con Google Sheets API usando un archivo de credenciales.
    Args:
        credentials_path (str): Ruta al archivo de credenciales JSON.
    Returns:
        gspread.Client: Cliente autenticado para acceder a Google Sheets.
    """
    try:
        creds = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Error durante la autenticación con Google Sheets: {e}")
        return None
