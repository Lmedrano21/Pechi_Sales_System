import json
import os
import sys
import threading
import http.server
import socketserver
import webbrowser
import urllib.parse
from datetime import datetime
import time

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS Y VARIABLES
# ==========================================

def resource_path(relative_path):
    """ Obtiene la ruta absoluta de un recurso, funciona para dev y para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def data_path(relative_path):
    """ Obtiene la ruta para archivos de datos (siempre fuera del EXE empaquetado) """
    if getattr(sys, 'frozen', False):
        # La aplicación se ejecuta como un bundle (.exe)
        base_path = os.path.dirname(sys.executable)
    else:
        # La aplicación se ejecuta como un script (.py)
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ARCHIVO_BD_HELADOS = data_path("inventario_helados.json")
ARCHIVO_BD_CLIENTES = data_path("clientes.json")
ARCHIVO_BD_FACTURAS = data_path("facturas.json")

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
def cargar_json(ruta, default):
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return default

def inicializar_sistemas():
    """Carga los datos iniciales y asegura que los archivos existan en la carpeta de datos."""
    global CATALOGO, CLIENTES, FACTURAS
    
    # 1. Cargar Catálogo (Si no existe, intentar copiar el bundled o usar inicial)
    if not os.path.exists(ARCHIVO_BD_HELADOS):
        # Intentamos ver si hay uno empaquetado (como plantilla)
        plantilla = resource_path("inventario_helados.json")
        if os.path.exists(plantilla):
            with open(plantilla, "r", encoding="utf-8") as f:
                CATALOGO = json.load(f)
        else:
            CATALOGO = CATALOGO_INICIAL.copy()
        guardar_inventario()
    else:
        CATALOGO = cargar_json(ARCHIVO_BD_HELADOS, CATALOGO_INICIAL.copy())

    # 2. Cargar Clientes
    if not os.path.exists(ARCHIVO_BD_CLIENTES):
        CLIENTES = {}
        guardar_clientes()
    else:
        CLIENTES = cargar_json(ARCHIVO_BD_CLIENTES, {})

    # 3. Cargar Facturas
    if not os.path.exists(ARCHIVO_BD_FACTURAS):
        FACTURAS = []
        guardar_facturas()
    else:
        FACTURAS = cargar_json(ARCHIVO_BD_FACTURAS, [])

def guardar_json(ruta, datos):
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error guardando {ruta}: {e}")

def guardar_inventario():
    guardar_json(ARCHIVO_BD_HELADOS, CATALOGO)

def guardar_clientes():
    guardar_json(ARCHIVO_BD_CLIENTES, CLIENTES)

def guardar_facturas():
    guardar_json(ARCHIVO_BD_FACTURAS, FACTURAS)

# Inicialización al importar
inicializar_sistemas()

# ==========================================
# 3. MÓDULO DE INVENTARIO Y CATÁLOGO
# ==========================================
def obtener_lista_sabores():
    return sorted(list(CATALOGO.keys()))

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

def fijar_stock(sabor, nueva_cantidad):
    if sabor not in CATALOGO:
        raise ValueError("Sabor no encontrado en el catálogo.")
    try:
        cantidad = int(nueva_cantidad)
    except ValueError:
        raise ValueError("La cantidad debe ser un número entero.")
    if cantidad < 0:
        raise ValueError("La cantidad no puede ser negativa.")
        
    CATALOGO[sabor]["stock"] = cantidad
    guardar_inventario()

def registrar_producto(sabor, costo, precio, stock_inicial):
    if sabor in CATALOGO:
        raise ValueError("El producto ya existe.")
    try:
        c = float(costo)
        p = float(precio)
        s = int(stock_inicial)
    except ValueError:
        raise ValueError("Costo, Precio y Stock deben ser números válidos.")
    
    CATALOGO[sabor] = {"costo": c, "precio": p, "stock": s}
    guardar_inventario()

def editar_producto(sabor_actual, nuevo_sabor, nuevo_costo, nuevo_precio):
    if sabor_actual not in CATALOGO:
        raise ValueError("El producto no existe.")
    
    try:
        c = float(nuevo_costo)
        p = float(nuevo_precio)
    except ValueError:
        raise ValueError("Costo y Precio deben ser números válidos.")

    # Si se cambió el nombre del sabor
    if nuevo_sabor != sabor_actual:
        if nuevo_sabor in CATALOGO:
            raise ValueError("El nuevo nombre ya está en uso.")
        # Mover los datos al nuevo nombre
        datos = CATALOGO.pop(sabor_actual)
        CATALOGO[nuevo_sabor] = datos
        sabor_actual = nuevo_sabor

    CATALOGO[sabor_actual]["costo"] = c
    CATALOGO[sabor_actual]["precio"] = p
    guardar_inventario()

def eliminar_producto(sabor):
    if sabor not in CATALOGO:
        raise ValueError("El producto no existe.")
    del CATALOGO[sabor]
    guardar_inventario()

# ==========================================
# 4. MÓDULO DE CLIENTES
# ==========================================
def obtener_clientes():
    return CLIENTES

def registrar_cliente(documento, nombre, telefono, direccion):
    if not documento.strip() or not nombre.strip() or not telefono.strip() or not direccion.strip():
        raise ValueError("Todos los campos son obligatorios.")
    if documento in CLIENTES:
        raise ValueError(f"Ya existe un cliente con el documento {documento}.")
    
    CLIENTES[documento] = {"nombre": nombre, "telefono": telefono, "direccion": direccion}
    guardar_clientes()

def editar_cliente(documento, nuevo_nombre, nuevo_telefono, nueva_direccion):
    if not documento.strip() or not nuevo_nombre.strip() or not nuevo_telefono.strip() or not nueva_direccion.strip():
        raise ValueError("Todos los campos son obligatorios.")
    if documento not in CLIENTES:
        raise ValueError(f"No existe un cliente con el documento {documento}.")
    
    CLIENTES[documento] = {"nombre": nuevo_nombre, "telefono": nuevo_telefono, "direccion": nueva_direccion}
    guardar_clientes()

def eliminar_cliente(documento):
    if documento not in CLIENTES:
        raise ValueError(f"No existe un cliente con el documento {documento}.")
    del CLIENTES[documento]
    guardar_clientes()

# ==========================================
# 5. MÓDULO DE VENTAS Y FACTURACIÓN
# ==========================================
def procesar_venta(sabor_seleccionado, cantidad_input, metodo_pago="Efectivo"):
    """Calcula el total, descuenta el stock y guarda la venta anónima."""
    detalle = cotizar_item(sabor_seleccionado, cantidad_input)
    
    # 1. Descontamos el inventario
    CATALOGO[sabor_seleccionado]["stock"] -= detalle['cantidad']
    guardar_inventario()
    
    # 2. Generamos la factura anónima
    factura_anonima = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cliente_documento": "00000000",
        "cliente_nombre": "Cliente Casual",
        "metodo_pago": metodo_pago,
        "total_venta": detalle['venta_total'],
        "total_costo": detalle['costo_total'],
        "utilidad": detalle['ganancia'],
        "detalle_productos": [{
            "sabor": detalle['sabor'],
            "cantidad": detalle['cantidad'],
            "costo_total": detalle['costo_total'],
            "venta_total": detalle['venta_total']
        }]
    }
    FACTURAS.append(factura_anonima)
    guardar_facturas()
    
    return detalle

def cotizar_item(sabor, cantidad_input):
    if sabor not in CATALOGO:
        raise ValueError("Selecciona un sabor válido.")
    try:
        cantidad = int(cantidad_input)
    except ValueError:
        raise ValueError("La cantidad debe ser un número entero.")
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a cero.")
        
    stock_actual = CATALOGO[sabor]["stock"]
    if cantidad > stock_actual:
        raise ValueError(f"Stock insuficiente para {sabor}. Quedan {stock_actual} unidades.")
    
    costo_t = CATALOGO[sabor]["costo"] * cantidad
    venta_t = CATALOGO[sabor]["precio"] * cantidad
    
    return {
        "sabor": sabor, "cantidad": cantidad,
        "costo_total": costo_t, "venta_total": venta_t, "ganancia": (venta_t - costo_t)
    }

def procesar_factura_completa(documento_cliente, carrito, metodo_pago="Efectivo"):
    if documento_cliente not in CLIENTES:
        raise ValueError("El cliente seleccionado no es válido.")
        
    # Doble verificación de stock
    for item in carrito:
        if CATALOGO[item["sabor"]]["stock"] < item["cantidad"]:
            raise ValueError(f"Falta stock de {item['sabor']}.")

    total_venta = 0
    total_costo = 0
    for item in carrito:
        sabor = item["sabor"]
        CATALOGO[sabor]["stock"] -= item["cantidad"]
        total_venta += item["venta_total"]
        total_costo += item["costo_total"]

    guardar_inventario()

    nueva_factura = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cliente_documento": documento_cliente,
        "cliente_nombre": CLIENTES[documento_cliente]["nombre"],
        "metodo_pago": metodo_pago,
        "total_venta": total_venta,
        "total_costo": total_costo,
        "utilidad": total_venta - total_costo,
        "detalle_productos": carrito
    }
    FACTURAS.append(nueva_factura)
    guardar_facturas()
    return nueva_factura

# ==========================================
# 6. MÓDULO DE SERVIDOR WEB (DASHBOARD)
# ==========================================
servidor_activo = False

class MiManejadorHTTP(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            ruta_solicitada = urllib.parse.unquote(self.path).split('?')[0]
            if ruta_solicitada == '/': ruta_solicitada = '/index.html'
            
            # Las peticiones JSON (datos) van a la carpeta de datos (junto al EXE)
            # Todo lo demás (HTML, JS, CSS) va a la carpeta de recursos (empaquetado)
            if ruta_solicitada.endswith('.json'):
                ruta_completa = data_path(ruta_solicitada.lstrip('/'))
            else:
                ruta_completa = resource_path(ruta_solicitada.lstrip('/'))
            
            if os.path.isfile(ruta_completa):
                with open(ruta_completa, 'rb') as f:
                    contenido = f.read()
                self.send_response(200)
                self.send_type_headers(ruta_completa)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Content-Length', len(contenido))
                self.end_headers()
                self.wfile.write(contenido)
            else:
                self.send_error(404, "Archivo no encontrado")
        except Exception as e:
            print(f"Error servidor: {e}")
            try: self.send_error(500, str(e))
            except: pass
    
    def send_type_headers(self, path):
        types = {'.json': 'application/json', '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css'}
        ext = os.path.splitext(path)[1]
        self.send_header('Content-type', f"{types.get(ext, 'application/octet-stream')}; charset=utf-8")

    def log_message(self, format, *args): pass

def lanzar_dashboard():
    global servidor_activo
    if not servidor_activo:
        def arrancar_servidor():
            try:
                socketserver.TCPServer.allow_reuse_address = True
                with socketserver.TCPServer(("", 8000), MiManejadorHTTP) as httpd:
                    httpd.serve_forever()
            except Exception as e: print(f"Error servidor x: {e}")

        threading.Thread(target=arrancar_servidor, daemon=True).start()
        servidor_activo = True
        time.sleep(1)
    webbrowser.open("http://localhost:8000")

# ==========================================
# 7. COMUNICACIÓN Y EXPORTACIÓN
# ==========================================
def enviar_factura_whatsapp(documento_cliente, carrito, total_venta):
    if documento_cliente not in CLIENTES:
        raise ValueError("Cliente no encontrado.")
        
    telefono = CLIENTES[documento_cliente]["telefono"]
    nombre = CLIENTES[documento_cliente]["nombre"]
    if not (telefono.startswith("57") or telefono.startswith("+57")):
        telefono = "57" + telefono
    telefono = telefono.replace("+", "").strip()

    mensaje = f"🍦 *HELADERÍA POS* 🍦\nHola _{nombre}_, resumen pedido:\n\n"
    for item in carrito:
        mensaje += f"▪️ {item['cantidad']}x {item['sabor']}: ${item['venta_total']:,}\n"
    mensaje += f"\n💰 *TOTAL: ${total_venta:,}*\n¡Gracias!"

    webbrowser.open(f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}")

def obtener_facturas():
    return FACTURAS

def anular_factura(fecha_id):
    global FACTURAS
    factura = next((f for f in FACTURAS if f["fecha"] == fecha_id), None)
    if not factura:
        raise ValueError("Factura no encontrada.")
        
    for item in factura["detalle_productos"]:
        if item["sabor"] in CATALOGO:
            CATALOGO[item["sabor"]]["stock"] += item["cantidad"]
            
    FACTURAS.remove(factura)
    guardar_inventario()
    guardar_facturas()

def exportar_factura_txt(fecha_id):
    factura = next((f for f in FACTURAS if f["fecha"] == fecha_id), None)
    if not factura: raise ValueError("Factura no encontrada.")
        
    nombre_archivo = f"Factura_{fecha_id.replace(':', '-').replace(' ', '_')}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("="*40 + "\n          HELADERÍA POS\n" + "="*40 + "\n")
        f.write(f"FECHA: {factura['fecha']}\nCLIENTE: {factura['cliente_nombre']}\nDOC: {factura['cliente_documento']}\n" + "-"*40 + "\n")
        f.write("CANT  | PRODUCTO                  | TOTAL\n" + "-"*40 + "\n")
        for item in factura["detalle_productos"]:
            f.write(f"{item['cantidad']:<5} | {item['sabor']:<23} | ${item['venta_total']:,}\n")
        f.write("-" * 40 + f"\nTOTAL PAGADO:                 ${factura['total_venta']:,}\n" + "="*40 + "\n      ¡Gracias por su compra!\n")
    os.startfile(nombre_archivo)