from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import browser_automation
import time

# Asegurarse de que el navegador esté configurado
#driver = browser_automation.driver   # asume que ya lo inicializaste en main.py

# Instancia global de WebDriver, inicializada al importar browser_automation
driver = browser_automation.driver # en vez de usar setup_broswer()
# ni idea, pero deberemos cambiar a objetos

if driver is None:
    raise RuntimeError("WebDriver no inicializado. Asegúrate de importar browser_automation para iniciar el navegador.")


def login_to_system():
    print("1. Introducción de credenciales")

    driver = browser_automation.driver
    if driver is None:
        raise RuntimeError("Driver no inicializado. Llama a setup_browser() antes de login_to_system.")
    print("1. Introducción de credenciales")

    try:
        print("     Iniciando...")
        driver.get("https://api-seguridad.sunat.gob.pe/v1/clientessol/4f3b88b3-d9d6-402a-b85d-6a0bc857746a/oauth2/loginMenuSol?originalUrl=https://e-menu.sunat.gob.pe/cl-ti-itmenu/AutenticaMenuInternet.htm&state=rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAx3CAAAABAAAAADdAAEZXhlY3B0AAZwYXJhbXN0AEsqJiomL2NsLXRpLWl0bWVudS9NZW51SW50ZXJuZXQuaHRtJmI2NGQyNmE4YjVhZjA5MTkyM2IyM2I2NDA3YTFjMWRiNDFlNzMzYTZ0AANleGVweA==")  # Reemplaza con la URL correcta  # URL completa
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtRuc"))
        ).send_keys("20602813712")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtUsuario"))
        ).send_keys("MAXIEIRL")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtContrasena"))
        ).send_keys("aquino18")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Iniciar sesión"]'))
        ).click()
        print("     Se logro introduccion de credenciales")
    except Exception as e:
        print(f"Error al iniciar sesión: {e}")
        raise

def navigate_to_invoice_section():
    print("2. Navegacion hasta seccion de facturas")
    """
    Navega hasta la sección de facturas en el sistema.
    Args:
        driver: WebDriver de Selenium.
    """
    try:
        print("     Empezando el 2...")
        # Navegar por el menú principal
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "divOpcionServicio2"))).click()
        print("     #1")
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "nivel1_11"))).click()
        print("     #2")
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "nivel2_11_5"))).click()
        print("     #3")
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "nivel3_11_5_3"))).click()
        print("     #4")
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "nivel4_11_5_3_1_1"))).click()
        print("     #5 cambiando de iframe")

        # Cambiar el foco al iframe de la aplicación de facturación
        iframe = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "iframeApplication"))
        )
        driver.switch_to.frame(iframe)
        print("     se logro navegacion y cambio de iframe")

    except Exception as e:
        print(f"Error al navegar a la sección de facturas: {e}")
        raise



def navigate_to_invoice_section2():
    print("2. Navegacion hasta seccion de facturas")
    """
    Navega hasta la sección de facturas en el sistema.
    Args:
        driver: WebDriver de Selenium.
    """
    try:
        print("     Empezando el 2...")
        # Navegar por el menú principal
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "divOpcionServicio2"))).click()
        print("     #1")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "nivel1_11"))).click()
        print("     #2")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "nivel2_11_5"))).click()
        print("     #3")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "nivel3_11_5_3"))).click()
        print("     #4")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "nivel4_11_5_3_1_1"))).click()
        print("     #5 cambiando de iframe")
        # Cambiar el foco al iframe de la aplicación de facturación
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "iframeApplication"))
        )
        driver.switch_to.frame(iframe)
        print("     se logro navegacion y cambio de iframe")
    ################################
    # cambio a IFRAME
    ################################

    except Exception as e:
        print(f"Error al navegar a la sección de facturas: {e}")
        raise


def input_client_data(ruc_cliente):
    print("3. Ingresamos datos del cliente")
    """
    Ingresa los datos del cliente en la sección de facturación.
    Args:
        driver: WebDriver de Selenium.
        ruc_cliente: Número RUC del cliente a ingresar.
    """
    try:
        # Ingresar el RUC del cliente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inicio.numeroDocumento"))).send_keys(ruc_cliente)

        # Seleccionar tipo de emisión y confirmar
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "inicio.subTipoEstEmi00"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "inicio.botonGrabarDocumento"))).click()
        print("     Se logro introducir ruc del cliente")

    except Exception as e:
        print(f"Error al ingresar datos del cliente: {e}")
        raise


def add_data_guia(serie, numero):
    """
    Agrega una guía relacionada (serie y número) a la sección de documentos relacionados.
    """
    try:
        print("7.1.agregamos serie")
        serie_documento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "docrel.serieDocumento"))
        )
        print("7.1.agregamos numero")
        serie_documento.clear()
        serie_documento.send_keys(serie)

        numero_documento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "docrel.numeroDocumentoInicial"))
        )
        numero_documento.clear()
        numero_documento.send_keys(numero)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "docrel.botonAddDoc"))
        ).click()

        print(f"Guía agregada: Serie {serie}, Número {numero}")
    except Exception as e:
        print(f"Error al agregar guía: {e}")
        raise

def add_observations(observation_text, guias):
    """
    Agrega observaciones generales y guías relacionadas a la factura antes de emitir.
    """
    print("5. Agregar observaciones")
    try:
        print("5.0")
        # 1) Click en guardar preliminar
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "factura.botonGrabarDocumento"))
        ).click()
        print("5.1")

        # 2) Escribir la observación
        observaciones_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "docsrel.observacion")) #  , widget_docsrel.observacion
        )# el ID esaba mal
        print("5.2")

        observaciones_element.clear()
        print("5.2.5")
        observaciones_element.send_keys(str(observation_text))
        print("5.3")

        if guias:
            print("5.4")
            # 3) Si hay guías, añadirlas antes de finalizar
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "docsrel.botonOtrosDocsRelacionados_label"))).click()
            print("5.5")
            # 5) Abrir el ComboBox de Tipo Documento
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,'//*[@id="widget_docrel.tipoDocumento"]/div[1]'))
            ).click()
            print("5.6")

            # 6) Esperar a que aparezca el popup y elegir la opción deseada
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[@id='docrel.tipoDocumento_popup']" +
                    "//div[@role='option' and normalize-space(.)='GUIA DE REMISION REMITENTE']"
                ))
            ).click()
            print("5.7")
            for guia in guias:
                # tu función que mete serie + número
                add_data_guia(guia["serie"], guia["numero"])

        print("6")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "docrel.botonAceptar")) # docrel.botonAceptar_label
        ).click()
        # 5) Aceptar las guías recién añadidas
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "docsrel.botonGrabarDocumento")) # docrel.botonAceptar_label
        ).click()
        print("7")

        print(f"Observación '{observation_text}' y guías agregadas correctamente.")
    except Exception as e:
        print(f"Error al agregar observaciones: {e}")
        raise


def confirm_invoice_emission():
    # Al llamar esta funcion, de frente ACEPTA la emsion, ya no hay un condicional
    print("--- codigo de confirmacion")
    """
    Muestra un mensaje interactivo para confirmar la emisión de la factura.
    Args:
        driver: WebDriver de Selenium.
    """
    try:


        # Confirmar factura
        #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "factura.botonGrabarDocumento"))).click()
        #print("Factura generada con éxito.")
        #factura.botonGrabarDocumento_label

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "factura-preliminar.botonGrabarDocumento"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "dlgBtnAceptarConfirm_label"))).click()
        print("Factura emitida con éxito.")
        time.sleep(5)  # Ajustar según la velocidad de descarga
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Descargar PDF"]'))).click()

    except Exception as e:
        print(f"Error al confirmar la emisión de la factura: {e}")
        raise


def obtener_importe_total():
    print("Obteniendo el importe total desde la página...")
    try:
        # Esperar a que el elemento con id "global.importeTotal" esté presente en el DOM
        WebDriverWait(driver, timeout=30).until(
            EC.presence_of_element_located((By.ID, "global.importeTotal"))
        )

        # Usar Selenium para localizar el elemento y obtener su atributo "value"
        elemento_importe_total = driver.find_element(By.ID, "global.importeTotal")
        importe_total = elemento_importe_total.get_attribute("value")

        print(f"El importe total obtenido es: {importe_total}")
        return importe_total
    except Exception as e:
        print(f"Error al obtener el importe total: {e}")
        return None


    except Exception as e:
        print(f"Error al obtener el importe total: {e}")
        return None


def create_invoice(items):
    print("4. Agregamos los items")

    """
    Crea una factura con los datos del cliente y los ítems especificados.
    Args:
        driver: WebDriver de Selenium.
        ruc_cliente: Número RUC del cliente.
        items: Lista de ítems a agregar a la factura.
    """
    try:

        # Validar que 'items' contiene datos
        if not items:
            raise ValueError("La lista de ítems está vacía o es inválida.")

        # Agregar ítems a la factura
        for item in items:
            # Botón para adicionar un ítem
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "factura.addItemButton"))).click()
            # Seleccionar tipo de ítem: Bien
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "item.subTipoTI01"))).click()

            # Ingresar cantidad
            cantidad_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "item.cantidad")))
            cantidad_element.clear()
            cantidad_element.send_keys(str(item["CANT"]))

            # Ingresar descripción del producto
            descripcion_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "item.descripcion")))
            descripcion_element.clear()
            descripcion_element.send_keys(item["DESCRIPCION"])

            # Calcular precio neto (sin IGV) y redondear a 8 decimales
            precio_sin_igv = float(item["P.UNIT"])
            precio_neto = round(precio_sin_igv / 1.18, 8)
            precio_formateado = f"{precio_neto:.8f}"

            # Ingresar precio unitario sin IGV
            precio_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "item.precioUnitario")))
            precio_element.clear()
            precio_element.send_keys(precio_formateado)
            time.sleep(0.5)
            precio_element.send_keys("\t")  # Simula un Tab para validar el campo

            # Confirmar adición del ítem
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "item.botonAceptar_label"))).click()


            ############ Asegurarse de que el sistema procese el ítem antes de continuar
            #WebDriverWait(driver, 10).until(lambda d: d.find_element(By.ID, "global.importeTotal").get_attribute("value").strip() != "")
            #time.sleep(1)  # Agregar un tiempo adicional para estabilizar el DOM
            #####
            # Obtener el importe parcial (para depuración)
            #parcial = driver.find_element(By.ID, "global.importeTotal").get_attribute("value")
            #print(f"Importe parcial después de agregar ítem: {parcial}")
            #######################

            ############ Asegurarse de que el sistema procese el ítem antes de continuar
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "global.importeTotal").get_attribute("value").strip() != ""
        )
        time.sleep(1)  # Agregar un tiempo adicional para estabilizar el DOM
        #####
        print("Todos los ítems fueron agregados correctamente.")

        #######################################
        #importe_total = obtener_importe_total()
        #return importe_total
        ########################################


        # Confirmar factura
        #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "factura.botonGrabarDocumento"))).click()
        #print("Factura generada con éxito.")
        #factura.botonGrabarDocumento_label
        # Llamar a la función para agregar observaciones
        #add_observations("AL CONTADO") # este bota el error, cuando diciendo : error al agregar observaciones!
        #print("se agrego los comentarios!")

        # Llamar a la función para confirmar la emisión
        #confirm_invoice_emission(driver)  ahora ello esta en el main!!!!!!

    except Exception as e:
        print(f"Error al agregar la factura: {e}")
        raise



