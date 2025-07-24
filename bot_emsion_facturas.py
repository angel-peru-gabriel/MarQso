import telebot
import os # para la busqueda
from telebot import types
from main import main_hasta_items
from file_operations import esperar_archivo_Abuscar, rename_and_move_file, read_sheet_data # para la busque y no redundar codigo
from invoice_operations2 import confirm_invoice_emission, add_observations,obtener_importe_total
import pandas as pd
from tabulate import tabulate  # Para un formato de tabla más legible

# Configuración del bot
TOKEN = '8055516526:AAGNJ_tRmL5lGVhwBEhnCXunJGWvE8vdTtU'
bot = telebot.TeleBot(TOKEN)

# Ruta del archivo CSV
CSV_PATH = r"C:\Users\Aquino\PycharmProjects\AQUINO_SELENIUM\facturas.csv"
# Ruta donde se busca el pdf
dir_Abuscar = r"C:\Users\Aquino\Documents\ademas\FAC\automatico"
download_folder = r"C:\Users\Aquino\Downloads"
destination_folder = r"C:\Users\Aquino\Documents\ademas\FAC\automatico"

# Comando /start para mostrar los comandos disponibles
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print("     Comando /start")
    comandos = """
👋 ¡Bienvenido! Aquí están los comandos que puedes usar:

1️⃣ /mostrar - Mostrar el contenido del archivo CSV.
2️⃣ /modificar - Modificar un valor del archivo CSV.
3️⃣ /emitir- Emitir una factura basada en los datos del CSV.

Usa cualquiera de estos comandos para interactuar con el bot. 😊
    """
    bot.reply_to(message, comandos)

# Función para procesar la confirmación del usuario
def process_confirmation(message, ruc_cliente):
    """
    Procesa la confirmación del usuario (si/no) para emitir la factura.
    """
    try:
        if message.text.lower() == "si":
            #######################################
            # Confirmar emisión de factura
            add_observations("AL CONTADO")  # Agregar observaciones
            confirm_invoice_emission()  # Se asume que devuelve True o False
            #######################################
            bot.reply_to(message, "✅ Factura emitida con éxito.")
            # Renombrar y mover el archivo generado
            name_pdf = rename_and_move_file(download_folder, destination_folder)
            print(f"Nombre del archivo generado: {name_pdf}")

            # Buscar el archivo PDF generado
            archivo_encontrado = esperar_archivo_Abuscar(dir_Abuscar, name_pdf)
            if archivo_encontrado:
                ruta_archivo = os.path.join(dir_Abuscar, archivo_encontrado)
                with open(ruta_archivo, "rb") as pdf:
                    bot.send_document(message.chat.id, pdf)
            else:
                bot.reply_to(message, "❌ No se encontró el archivo PDF generado.")
        else:
            # El usuario canceló la emisión de la factura
            bot.reply_to(message, "❌ Emisión de factura cancelada. Enviando PDF de prueba.")
            # Enviar un PDF de prueba
            ruta_prueba = r"C:\Users\Aquino\Documents\ademas\FAC\automatico\E001-3532 ASCENSORES Y MONTACARGAS MELENDES E.I.R.L..pdf"
            if os.path.exists(ruta_prueba):
                with open(ruta_prueba, "rb") as pdf:
                    bot.send_document(message.chat.id, pdf)
            else:
                bot.reply_to(message, "❌ No se encontró el archivo de prueba para enviar.")

    except Exception as e:
        # Manejo de excepciones y notificación al usuario
        bot.reply_to(message, f"❌ Error al procesar la confirmación: {str(e)}")


# Comando /emitir
@bot.message_handler(commands=['emitir'])
def handle_emitir_factura(message):
    """
    Comando para emitir una factura. Solicita confirmación al usuario.
    """
    try:
        print("     Comando 3. /emitir")

        # Dividir el mensaje para obtener el RUC
        partes = message.text.split()
        if len(partes) != 2:
            bot.reply_to(message, "❌ Formato incorrecto. Usa: /emitir <RUC>. Ejemplo: /emitir 20605841318")
            return

        # Extraer el RUC del mensaje
        ruc_cliente = partes[1]

        # Validar que el RUC tenga el formato correcto (11 dígitos)
        if not ruc_cliente.isdigit() or len(ruc_cliente) != 11:
            bot.reply_to(message, "❌ RUC inválido. Debe contener 11 dígitos numéricos.")
            return
        # Mensaje inicial
        bot.reply_to(message, f"⚙️ Iniciando la emisión de la factura para el RUC: {ruc_cliente}. Por favor, espera...")


        ########################
        main_hasta_items(ruc_cliente)
        MONTO= obtener_importe_total()
        ########################
        # muestra el monto por telegram, segun esta respuesta
        bot.reply_to(message, f"El monto es:{MONTO}")
        #########################

        # Pedir confirmación al usuario
        bot.reply_to(message, "¿Confirmas la emisión de la factura? Responde con 'si' o 'no'.")
        bot.register_next_step_handler(message, process_confirmation, ruc_cliente)

    except Exception as e:
        bot.reply_to(message, f"❌ Error al iniciar el proceso de emisión: {str(e)}")


# Comando para mostrar todo el contenido del Excel (Google Sheets)
@bot.message_handler(commands=['mostrar'])
def mostrar_excel(message):
    try:
        print("Comando 1. /mostrar")

        # Leer los datos desde Google Sheets
        sheet_name = "fracturas"  # Nombre de la hoja de cálculo
        records = read_sheet_data(sheet_name)

        # Verificar que se hayan cargado registros
        if not records:
            bot.reply_to(message, text="❌ No se encontraron datos en la hoja de cálculo.")
            return

        # Usar tabulate para crear una tabla legible
        from tabulate import tabulate
        texto = tabulate(records, headers="keys", tablefmt="grid", showindex=True)

        # Dividir en bloques si el mensaje es muy largo (Telegram tiene límite de caracteres)
        for i in range(0, len(texto), 4000):
            bot.reply_to(message, text=f"📊 Datos del Excel (Parte {i // 4000 + 1}):\n\n{texto[i:i + 4000]}")

    except Exception as e:
        bot.reply_to(message, text=f"❌ Error al leer la hoja de cálculo: {str(e)}")



# Comando para modificar un valor en el CSV
@bot.message_handler(commands=['modificar'])
def modificar_csv(message):
    """
    Formato del comando: /modificar fila columna nuevo_valor
    Ejemplo: /modificar 1 Precio 150.00
    """
    try:
        print("     Comando 3. /modificar")
        # Dividir el mensaje para obtener los argumentos
        partes = message.text.split()
        if len(partes) < 4:
            bot.reply_to(message, "❌ Formato incorrecto. Ejemplo: /modificar 1 Precio 150.00")
            return

        # Parámetros: fila, columna y nuevo valor
        fila = int(partes[1]) - 1  # Telegram usa base 1, pero Pandas usa base 0
        columna = partes[2].upper()  # Convertir el nombre de la columna a mayúsculas
        nuevo_valor = partes[3]

        # Leer el archivo CSV
        df = pd.read_csv(CSV_PATH)

        # Validar existencia de la fila y columna
        if fila < 0 or fila >= len(df) or columna not in df.columns:
            bot.reply_to(message, f"❌ Fila o columna no válidas. Verifica tu entrada.")
            return

        # Actualizar el valor en la celda correspondiente
        df.at[fila, columna] = nuevo_valor

        # Guardar los cambios en el archivo CSV
        df.to_csv(CSV_PATH, index=False)

        # Confirmar la actualización
        bot.reply_to(message, f"✅ Se actualizó la fila {fila + 1}, columna '{columna}' a: {nuevo_valor}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error al modificar el archivo CSV: {str(e)}")




if __name__ == "__main__":
    print("Iniciando el bot...")
    bot.polling(none_stop=True)
