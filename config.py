from dotenv import load_dotenv
import os
load_dotenv() # carga el archivo .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUNAT_RUC  = os.getenv("SUNAT_RUC")
SUNAT_USER = os.getenv("SUNAT_USER")
SUNAT_PASS = os.getenv("SUNAT_PASS")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# Cada variable definida en el archivo .env se carga aquí como una variable de entorno
# y puede ser utilizada en el resto del código SOLO importandolas
# eso son variables globales # que se pueden usar en cualquier parte del proyecto sin necesidad de pasarlas como parámetros O.O