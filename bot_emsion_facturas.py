import telebot
import os # para la busqueda
from telebot import types
from main import main_hasta_items
from file_operations import esperar_archivo_Abuscar, rename_and_move_file, read_sheet_data # para la busque y no redundar codigo
from invoice_operations2 import confirm_invoice_emission, add_observations,obtener_importe_total
# para la tabla de items
import pandas as pd
from tabulate import tabulate  # Para un formato de tabla más legible
# de utils
from API_authenticate import authenticate_google_sheets
from utils import Debouncer, RateLimiter, retry_with_backoff


# Configuración del bot
TOKEN = '8055516526:AAGNJ_tRmL5lGVhwBEhnCXunJGWvE8vdTtU'
bot = telebot.TeleBot(TOKEN)

# Guardamos estado por chat
sessions = {}

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

# Construye la tabla en ASCII y la envuelve en Markdown
def build_table_markdown(items):
    # items: lista de dicts con mismas keys, p.ej. [{"CANT":5,...},...]
    tabla = tabulate(items,
                     headers="keys",
                     tablefmt="grid",
                     showindex=range(1, len(items)+1))
    return f"```{tabla}```"

# Genera un teclado inline con un botón por fila
def build_edit_keyboard(items):
    kb = types.InlineKeyboardMarkup(row_width=3)
    botones = [
        types.InlineKeyboardButton(f"✏️ Editar fila {i+1}", callback_data=f"edit:{i}")
        for i in range(len(items))
    ]
    kb.add(*botones)
    return kb

# 1) Comando /items → muestra la tabla inicial
@bot.message_handler(commands=["items"])
def cmd_items(message):
    chat_id = message.chat.id
    items = read_sheet_data("fracturas")  # tu Google Sheet
    if not items:
        return bot.reply_to(message, "❌ No hay ítems aún.")
    text = build_table_markdown(items)
    kb   = build_edit_keyboard(items)
    sent = bot.send_message(chat_id, text,
                            parse_mode="Markdown",
                            reply_markup=kb)
    # Guardamos el mensaje y la lista para posteriores ediciones
    sessions[chat_id] = {
        "message_id": sent.message_id,
        "items": items
    }

# 2) Capturamos pulsación “✏️ Editar fila X”
@bot.callback_query_handler(func=lambda c: c.data.startswith("edit:"))
def on_edit_row(call):
    chat_id = call.message.chat.id
    idx = int(call.data.split(":")[1])
    sessions[chat_id]["edit"] = {"row": idx}
    # Preguntamos qué campo quiere editar
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("Cantidad",       callback_data=f"field:{idx}:CANT"),
        types.InlineKeyboardButton("Descripción",    callback_data=f"field:{idx}:DESCRIPCION"),
        types.InlineKeyboardButton("Precio Unitario",callback_data=f"field:{idx}:P.UNIT"),
    )
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id,
                     f"¿Qué campo de la fila {idx+1} quieres editar?",
                     reply_markup=kb)

# 3) Capturamos elección de campo
@bot.callback_query_handler(func=lambda c: c.data.startswith("field:"))
def on_field_selected(call):
    chat_id = call.message.chat.id
    _, idx_str, field = call.data.split(":")
    sessions[chat_id]["edit"]["field"] = field
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id,
                     f"Envía el *nuevo valor* para _{field}_ en la fila {int(idx_str)+1}.",
                     parse_mode="Markdown")
    # Preparamos el siguiente mensaje de texto para procesar el valor
    bot.register_next_step_handler_by_chat_id(chat_id, process_new_value)

# 4) Recibimos el nuevo valor, actualizamos y redibujamos la tabla
def process_new_value(message):
    chat_id = message.chat.id
    text    = message.text
    sess    = sessions.get(chat_id)
    if not sess or "edit" not in sess:
        return bot.reply_to(message, "❌ No hay edición en curso.")
    idx   = sess["edit"]["row"]
    field = sess["edit"]["field"]
    items = sess["items"]

    # Actualizamos el valor (puedes convertir a int/float si quieres)
    items[idx][field] = text

    # Redibujamos la tabla completa y reemplazamos el mensaje original
    new_md = build_table_markdown(items)
    new_kb = build_edit_keyboard(items)
    bot.edit_message_text(new_md,
                          chat_id,
                          sess["message_id"],
                          parse_mode="Markdown",
                          reply_markup=new_kb)

    # Confirmación y limpieza de estado
    bot.reply_to(message, f"✅ Fila {idx+1} actualizada: {field} = {text}")
    sess.pop("edit")




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


"""- Necesito la descripcion tenga salto de linea, para lograr en la app, no alterar el formato y obtener un buen acabado. """