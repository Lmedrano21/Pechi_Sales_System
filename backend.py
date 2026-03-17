import json
import os
import threading
import http.server
import socketserver
import webbrowser
import urllib.parse
import webbrowser
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS Y VARIABLES
# ==========================================
ARCHIVO_BD_HELADOS = "inventario_helados.json"
ARCHIVO_BD_CLIENTES = "clientes.json"
ARCHIVO_BD_FACTURAS = "facturas.json"

CATALOGO = {}
CLIENTES = {}
FACTURAS = []

CATALOGO_INICIAL = {
    "Mango Enchilado": {"costo": 700, "precio": 1500, "stock": 100},
    "Fusión de Sabores": {"costo": 893, "precio": 1600, "stock": 50},
    "Mango Super Ácido": {"costo": 688, "precio": 1700, "stock": 75},
    "Piña Enchilada": {"costo": 550, "precio": 1500, "stock": 60},
    "Fusión Tropical": {"costo": 830, "precio": 1700, "stock": 40},
    "Milo Cremoso": {"costo": 780, "precio": 2000, "stock": 30},
    "Mango Tamarindo": {"costo": 634, "precio": 1400, "stock": 80},
    "Mousse Maracuyá": {"costo": 950, "precio": 2000, "stock": 25},
    "Chicle Fantasía": {"costo": 740, "precio": 1800, "stock": 45},
    "Brownie": {"costo": 820, "precio": 2000, "stock": 35},
    "Fresa Crema": {"costo": 673, "precio": 2000, "stock": 40},
    "Frutas con Crema": {"costo": 1100, "precio": 2100, "stock": 20},
    "Gomiloco": {"costo": 1277, "precio": 2300, "stock": 15},
    "Helado Quipitos": {"costo": 1457, "precio": 2500, "stock": 10},
    "Mango Trolulu": {"costo": 720, "precio": 1500, "stock": 90},
    "Helado y Casa": {"costo": 1100, "precio": 2100, "stock": 25},
    "Mango Kiwi": {"costo": 800, "precio": 1600, "stock": 70},
    "Trisabor": {"costo": 786, "precio": 1400, "stock": 55},
    "Mango Pipop Chi": {"costo": 727, "precio": 1800, "stock": 60},
    "Mango Manzana": {"costo": 640, "precio": 1400, "stock": 75},
    "Chocorramo": {"costo": 720, "precio": 2000, "stock": 40},
    "Mango Piña": {"costo": 600, "precio": 1200, "stock": 80},
    "Mango Fresa": {"costo": 565, "precio": 1200, "stock": 90},
    "Mango Chamoy": {"costo": 800, "precio": 1500, "stock": 60},
    "Mango Biche": {"costo": 400, "precio": 900, "stock": 100},
    "Maracumango": {"costo": 400, "precio": 1000, "stock": 80},
    "Mango Lulo": {"costo": 590, "precio": 1600, "stock": 75},
    "Queso Bocadillo": {"costo": 800, "precio": 2100, "stock": 50},
    "Queso Arequipe": {"costo": 814, "precio": 2100, "stock": 45},
    "Veteado Mora": {"costo": 814, "precio": 2100, "stock": 55},
    "Super Coco": {"costo": 950, "precio": 2000, "stock": 35},
    "Fresa Cremoso": {"costo": 650, "precio": 1600, "stock": 70},
    "Oreo": {"costo": 800, "precio": 1800, "stock": 65},
    "Tropical": {"costo": 950, "precio": 2100, "stock": 40},
    "Capuchino R.": {"costo": 1004, "precio": 2000, "stock": 30},
    "Arequipe Brownie": {"costo": 950, "precio": 2100, "stock": 25},
    "Hershey": {"costo": 1440, "precio": 2300, "stock": 20},
    "Snicker": {"costo": 1050, "precio": 2100, "stock": 35},
    "Bon Bon Cremoso": {"costo": 880, "precio": 2100, "stock": 45},
    "Mix de Frutas": {"costo": 880, "precio": 1700, "stock": 50},
    "Piña Colada": {"costo": 1100, "precio": 2100, "stock": 40},
    "Mamón": {"costo": 600, "precio": 1500, "stock": 60},
    "Mango Bubals": {"costo": 806, "precio": 1600, "stock": 75},
    "Mango Mandar": {"costo": 600, "precio": 1300, "stock": 80},
    "Mango Bocadillo": {"costo": 650, "precio": 1400, "stock": 75}
}

# ==========================================
# 2. SISTEMA DE CARGA Y GUARDADO (PERSISTENCIA)
# ==========================================
def inicializar_sistemas():
    """Carga los tres archivos JSON a la memoria RAM al abrir el programa."""
    global CATALOGO, CLIENTES, FACTURAS
    
    # 1. Cargar Helados
    if os.path.exists(ARCHIVO_BD_HELADOS):
        try:
            with open(ARCHIVO_BD_HELADOS, "r", encoding="utf-8") as f:
                CATALOGO = json.load(f)
        except json.JSONDecodeError:
            CATALOGO = CATALOGO_INICIAL.copy()
            guardar_inventario()
    else:
        CATALOGO = CATALOGO_INICIAL.copy()
        guardar_inventario()

    # 2. Cargar Clientes
    if os.path.exists(ARCHIVO_BD_CLIENTES):
        try:
            with open(ARCHIVO_BD_CLIENTES, "r", encoding="utf-8") as f:
                CLIENTES = json.load(f)
        except json.JSONDecodeError:
            CLIENTES = {}
            guardar_clientes()
    else:
        CLIENTES = {}
        guardar_clientes()
        
    # 3. Cargar Facturas
    if os.path.exists(ARCHIVO_BD_FACTURAS):
        try:
            with open(ARCHIVO_BD_FACTURAS, "r", encoding="utf-8") as f:
                FACTURAS = json.load(f)
        except json.JSONDecodeError:
            FACTURAS = []
            guardar_facturas()
    else:
        FACTURAS = []
        guardar_facturas()

def guardar_inventario():
    with open(ARCHIVO_BD_HELADOS, "w", encoding="utf-8") as f:
        json.dump(CATALOGO, f, indent=4, ensure_ascii=False)

def guardar_clientes():
    with open(ARCHIVO_BD_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(CLIENTES, f, indent=4, ensure_ascii=False)

def guardar_facturas():
    with open(ARCHIVO_BD_FACTURAS, "w", encoding="utf-8") as f:
        json.dump(FACTURAS, f, indent=4, ensure_ascii=False)

# ¡DETONADOR! Se ejecuta apenas el backend se importa
inicializar_sistemas()

# ==========================================
# 3. MÓDULO DE INVENTARIO Y CATÁLOGO
# ==========================================
def obtener_lista_sabores():
    return list(CATALOGO.keys())

def obtener_inventario():
    return CATALOGO

def actualizar_stock(sabor, cantidad_a_sumar):
    if sabor not in CATALOGO:
        raise ValueError("Sabor no encontrado en el catálogo.")
    try:
        cantidad = int(cantidad_a_sumar)
    except ValueError:
        raise ValueError("La cantidad a sumar debe ser un número entero.")
    if cantidad <= 0:
        raise ValueError("Debes ingresar una cantidad mayor a cero.")
        
    CATALOGO[sabor]["stock"] += cantidad
    guardar_inventario()

# ==========================================
# 4. MÓDULO DE CLIENTES
# ==========================================
def obtener_clientes():
    return CLIENTES

def registrar_cliente(documento, nombre, telefono):
    if not documento.strip() or not nombre.strip() or not telefono.strip():
        raise ValueError("Todos los campos son obligatorios.")
    if documento in CLIENTES:
        raise ValueError(f"Ya existe un cliente con el documento {documento}.")
    
    CLIENTES[documento] = {
        "nombre": nombre,
        "telefono": telefono
    }
    guardar_clientes()

# ==========================================
# 5. MÓDULO DE VENTAS RÁPIDAS (CAJA ÚNICA)
# ==========================================
def procesar_venta(sabor_seleccionado, cantidad_input):
    """Calcula el total, descuenta el stock y guarda la venta anónima."""
    if sabor_seleccionado not in CATALOGO:
        raise ValueError("Por favor, selecciona un sabor válido.")
    try:
        cantidad = int(cantidad_input)
    except ValueError:
        raise ValueError("La cantidad debe ser un número entero.")
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a cero.")
        
    stock_actual = CATALOGO[sabor_seleccionado]["stock"]
    if cantidad > stock_actual:
        raise ValueError(f"Stock insuficiente. Quedan {stock_actual} unidades.")
    
    costo_t = CATALOGO[sabor_seleccionado]["costo"] * cantidad
    venta_t = CATALOGO[sabor_seleccionado]["precio"] * cantidad
    ganancia = venta_t - costo_t
    
    # 1. Descontamos el inventario
    CATALOGO[sabor_seleccionado]["stock"] -= cantidad
    guardar_inventario()
    
    # 2. Generamos la factura anónima para que aparezca en el Dashboard
    factura_anonima = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cliente_documento": "00000000",
        "cliente_nombre": "Cliente Casual",
        "total_venta": venta_t,
        "total_costo": costo_t,
        "utilidad": ganancia,
        "detalle_productos": [{
            "sabor": sabor_seleccionado,
            "cantidad": cantidad,
            "costo_total": costo_t,
            "venta_total": venta_t
        }]
    }
    FACTURAS.append(factura_anonima)
    guardar_facturas()
    
    return {
        "sabor": sabor_seleccionado, "cantidad": cantidad,
        "costo_total": costo_t, "venta_total": venta_t, "ganancia": ganancia
    }

# ==========================================
# 6. MÓDULO DE FACTURACIÓN (CARRITO Y PEDIDOS)
# ==========================================
def cotizar_item(sabor_seleccionado, cantidad_input):
    """Calcula el total para el carrito (NO descuenta stock aún)."""
    if sabor_seleccionado not in CATALOGO:
        raise ValueError("Por favor, selecciona un sabor válido.")
    try:
        cantidad = int(cantidad_input)
    except ValueError:
        raise ValueError("La cantidad debe ser un número entero.")
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a cero.")
        
    stock_actual = CATALOGO[sabor_seleccionado]["stock"]
    if cantidad > stock_actual:
        raise ValueError(f"Stock insuficiente. Quedan {stock_actual} unidades.")
    
    costo_t = CATALOGO[sabor_seleccionado]["costo"] * cantidad
    venta_t = CATALOGO[sabor_seleccionado]["precio"] * cantidad
    
    return {
        "sabor": sabor_seleccionado, "cantidad": cantidad,
        "costo_total": costo_t, "venta_total": venta_t, "ganancia": (venta_t - costo_t)
    }

def procesar_factura_completa(documento_cliente, carrito):
    """Descuenta el stock final y guarda el recibo detallado."""
    if documento_cliente not in CLIENTES:
        raise ValueError("El cliente seleccionado no es válido o no existe.")
        
    # Doble verificación de stock
    for item in carrito:
        if CATALOGO[item["sabor"]]["stock"] < item["cantidad"]:
            raise ValueError(f"Falta stock de {item['sabor']} (Quedan {CATALOGO[item['sabor']]['stock']}).")

    # Descontar el stock real
    total_venta_factura = 0
    total_costo_factura = 0
    
    for item in carrito:
        sabor = item["sabor"]
        CATALOGO[sabor]["stock"] -= item["cantidad"]
        total_venta_factura += item["venta_total"]
        total_costo_factura += item["costo_total"]

    guardar_inventario()

    # Generar factura con fecha
    nueva_factura = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cliente_documento": documento_cliente,
        "cliente_nombre": CLIENTES[documento_cliente]["nombre"],
        "total_venta": total_venta_factura,
        "total_costo": total_costo_factura,
        "utilidad": total_venta_factura - total_costo_factura,
        "detalle_productos": carrito
    }
    
    FACTURAS.append(nueva_factura)
    guardar_facturas()

# ==========================================
# 7. MÓDULO DE SERVIDOR WEB (DASHBOARD)
# ==========================================
servidor_activo = False

def lanzar_dashboard():
    global servidor_activo
    puerto = 8000

    if not servidor_activo:
        def arrancar_servidor():
            Handler = http.server.SimpleHTTPRequestHandler
            socketserver.TCPServer.allow_reuse_address = True
            try:
                with socketserver.TCPServer(("", puerto), Handler) as httpd:
                    httpd.serve_forever()
            except Exception as e:
                print(f"Error en el servidor: {e}")

        # Hilo en segundo plano para no congelar la ventana de Tkinter
        hilo_web = threading.Thread(target=arrancar_servidor, daemon=True)
        hilo_web.start()
        servidor_activo = True

    # Abrir el navegador automáticamente
    webbrowser.open(f"http://localhost:{puerto}")
    
def enviar_factura_whatsapp(documento_cliente, carrito, total_venta):
    # 1. Obtenemos el teléfono del diccionario de clientes
    if documento_cliente not in CLIENTES:
        raise ValueError("Cliente no encontrado.")
        
    telefono = CLIENTES[documento_cliente]["telefono"]
    nombre = CLIENTES[documento_cliente]["nombre"]
    
    # IMPORTANTE: WhatsApp requiere el código de país. 
    # Asumiendo que estamos en Colombia (+57), lo agregamos si no lo tiene.
    if not telefono.startswith("57") and not telefono.startswith("+57"):
        telefono = "57" + telefono
        
    # Limpiamos el símbolo '+' si lo tiene para la URL
    telefono = telefono.replace("+", "")

    # 2. Armamos el diseño del ticket usando formato de WhatsApp
    mensaje = f"🍦 *HELADERÍA POS* 🍦\n"
    mensaje += f"Hola _{nombre}_, gracias por tu compra.\n"
    mensaje += f"Aquí tienes el resumen de tu pedido:\n\n"
    
    for item in carrito:
        mensaje += f"▪️ {item['cantidad']}x {item['sabor']}: ${item['venta_total']:,}\n"
        
    mensaje += f"\n💰 *TOTAL A PAGAR: ${total_venta:,}*\n\n"
    mensaje += f"¡Esperamos verte pronto!"

    # 3. Convertimos el texto normal a texto codificado para URL (ej. espacios a %20)
    texto_codificado = urllib.parse.quote(mensaje)

    # 4. Creamos el link de WhatsApp Web
    # Cambiamos web.whatsapp.com por wa.me (es más directo y compatible)
    enlace_whatsapp = f"https://wa.me/{telefono}?text={texto_codificado}"

    # 5. Le decimos a Python que abra el navegador
    webbrowser.open(enlace_whatsapp)

# ==========================================
# 8. MÓDULO DE HISTORIAL Y ANULACIONES
# ==========================================
def obtener_facturas():
    """Devuelve la lista completa de facturas."""
    return FACTURAS

def anular_factura(fecha_id):
    """Busca la factura, regresa los helados al stock y elimina el registro."""
    global FACTURAS
    factura_objetivo = None
    
    # 1. Buscamos la factura por su fecha exacta
    for factura in FACTURAS:
        if factura["fecha"] == fecha_id:
            factura_objetivo = factura
            break
            
    if not factura_objetivo:
        raise ValueError("No se encontró la factura en la base de datos.")
        
    # 2. Devolvemos los productos al inventario
    for item in factura_objetivo["detalle_productos"]:
        sabor = item["sabor"]
        cantidad = item["cantidad"]
        # Validamos que el sabor siga existiendo en el catálogo
        if sabor in CATALOGO:
            CATALOGO[sabor]["stock"] += cantidad
            
    # Guardamos el inventario recuperado
    guardar_inventario()
    
    # 3. Eliminamos la factura del historial y guardamos
    FACTURAS.remove(factura_objetivo)
    guardar_facturas()

def exportar_factura_txt(fecha_id):
    """Crea un archivo de texto con el formato del recibo y lo abre."""
    factura_objetivo = None
    for factura in FACTURAS:
        if factura["fecha"] == fecha_id:
            factura_objetivo = factura
            break
            
    if not factura_objetivo:
        raise ValueError("No se encontró la factura.")
        
    # Limpiamos los dos puntos (:) porque Windows no permite guardar archivos con ese símbolo
    fecha_limpia = fecha_id.replace(":", "-").replace(" ", "_")
    nombre_archivo = f"Factura_{fecha_limpia}.txt"
    
    # Creamos y dibujamos el archivo de texto
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("="*40 + "\n")
        f.write("             HELADERÍA POS             \n")
        f.write("="*40 + "\n")
        f.write(f"FECHA: {factura_objetivo['fecha']}\n")
        f.write(f"CLIENTE: {factura_objetivo['cliente_nombre']}\n")
        f.write(f"DOCUMENTO: {factura_objetivo['cliente_documento']}\n")
        f.write("-" * 40 + "\n")
        f.write("CANT  | PRODUCTO                  | TOTAL\n")
        f.write("-" * 40 + "\n")
        
        for item in factura_objetivo["detalle_productos"]:
            # Formateo para que se vea alineado como un ticket real
            f.write(f"{item['cantidad']:<5} | {item['sabor']:<23} | ${item['venta_total']:,}\n")
            
        f.write("-" * 40 + "\n")
        f.write(f"TOTAL PAGADO:                 ${factura_objetivo['total_venta']:,}\n")
        f.write("="*40 + "\n")
        f.write("        ¡Gracias por su compra!        \n")
        
    # Le decimos a Windows que abra el bloc de notas automáticamente con este archivo
    os.startfile(nombre_archivo)
# Asegúrate de tener esto arriba en tu backend.py:
# import urllib.parse
# import webbrowser

def enviar_factura_whatsapp(documento_cliente, carrito, total_venta):
    if documento_cliente not in CLIENTES:
        raise ValueError("Cliente no encontrado.")
        
    telefono = CLIENTES[documento_cliente]["telefono"]
    nombre = CLIENTES[documento_cliente]["nombre"]
    
    # Agregamos el indicativo de Colombia (+57) si no lo tiene
    if not telefono.startswith("57") and not telefono.startswith("+57"):
        telefono = "57" + telefono
    telefono = telefono.replace("+", "")

    # Armamos el mensaje
    mensaje = f"🍦 *HELADERÍA POS* 🍦\n"
    mensaje += f"Hola _{nombre}_, gracias por tu compra.\n"
    mensaje += f"Aquí tienes el resumen de tu pedido:\n\n"
    
    for item in carrito:
        mensaje += f"▪️ {item['cantidad']}x {item['sabor']}: ${item['venta_total']:,}\n"
        
    mensaje += f"\n💰 *TOTAL A PAGAR: ${total_venta:,}*\n\n"
    mensaje += f"¡Esperamos verte pronto!"

    import urllib.parse
    import webbrowser
    texto_codificado = urllib.parse.quote(mensaje)
    enlace_whatsapp = f"https://wa.me/{telefono}?text={texto_codificado}"
    webbrowser.open(enlace_whatsapp)