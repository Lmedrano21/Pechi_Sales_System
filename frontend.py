import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import backend

# ==========================================
# VARIABLES GLOBALES
# ==========================================
acumulado_costo = 0.0
acumulado_ventas = 0.0
acumulado_ganancia = 0.0
carrito_actual = []

# ==========================================
# FUNCIONES: VENTAS RÁPIDAS
# ==========================================
def registrar_venta_rapida():
    global acumulado_costo, acumulado_ventas, acumulado_ganancia
    sabor = combo_ventas_sabores.get()
    cantidad_txt = entrada_ventas_cantidad.get()
    try:
        venta = backend.procesar_venta(sabor, cantidad_txt)
        tabla_ventas.insert("", "end", values=(venta['sabor'], venta['cantidad'], f"${venta['costo_total']:,}", f"${venta['venta_total']:,}"))
        acumulado_costo += venta['costo_total']
        acumulado_ventas += venta['venta_total']
        acumulado_ganancia += venta['ganancia']
        lbl_total_costo.config(text=f"Costo: ${acumulado_costo:,.0f}")
        lbl_total_ventas.config(text=f"Ingresos: ${acumulado_ventas:,.0f}")
        lbl_total_ganancia.config(text=f"Ganancia: ${acumulado_ganancia:,.0f}")
        combo_ventas_sabores.set(''); entrada_ventas_cantidad.delete(0, tk.END); combo_ventas_sabores.focus()
        recargar_inventario()
        recargar_historial_facturas() # Refrescamos la nueva pestaña
    except ValueError as e:
        messagebox.showwarning("Error en Venta", str(e))

# ==========================================
# FUNCIONES: INVENTARIO
# ==========================================
def recargar_inventario():
    for fila in tabla_inventario.get_children(): tabla_inventario.delete(fila)
    try:
        for sabor, datos in backend.obtener_inventario().items():
            tabla_inventario.insert("", "end", values=(sabor, datos.get("stock", 0)))
    except: pass

def guardar_ingreso():
    sabor = combo_inv_sabores.get()
    cantidad = entrada_inv_cantidad.get()
    try:
        backend.actualizar_stock(sabor, cantidad)
        messagebox.showinfo("Éxito", f"Stock de {sabor} actualizado.")
        combo_inv_sabores.set(''); entrada_inv_cantidad.delete(0, tk.END)
        recargar_inventario()
    except ValueError as e:
        messagebox.showwarning("Error", str(e))

# ==========================================
# FUNCIONES: CLIENTES
# ==========================================
def guardar_nuevo_cliente():
    doc = entrada_cli_doc.get()
    nom = entrada_cli_nom.get()
    tel = entrada_cli_tel.get()
    try:
        backend.registrar_cliente(doc, nom, tel)
        messagebox.showinfo("Éxito", "Cliente registrado.")
        entrada_cli_doc.delete(0, tk.END); entrada_cli_nom.delete(0, tk.END); entrada_cli_tel.delete(0, tk.END)
        recargar_clientes()
    except ValueError as e:
        messagebox.showwarning("Error", str(e))

def recargar_clientes():
    for fila in tabla_clientes.get_children(): tabla_clientes.delete(fila)
    try:
        clientes = backend.obtener_clientes()
        for doc, datos in clientes.items():
            tabla_clientes.insert("", "end", values=(doc, datos['nombre'], datos['telefono']))
        lista_nombres = [f"{doc} - {datos['nombre']}" for doc, datos in clientes.items()]
        combo_fac_cliente.config(values=lista_nombres)
    except: pass

# ==========================================
# FUNCIONES: FACTURACIÓN DETALLADA
# ==========================================
def agregar_al_carrito():
    sabor = combo_fac_sabores.get()
    cantidad_txt = entrada_fac_cantidad.get()
    try:
        item = backend.cotizar_item(sabor, cantidad_txt)
        carrito_actual.append(item)
        tabla_factura.insert("", "end", values=(item['sabor'], item['cantidad'], f"${item['venta_total']:,}"))
        total_factura = sum(x['venta_total'] for x in carrito_actual)
        lbl_total_factura.config(text=f"TOTAL: ${total_factura:,.0f}")
        combo_fac_sabores.set(''); entrada_fac_cantidad.delete(0, tk.END)
    except ValueError as e:
        messagebox.showwarning("Error", str(e))

def generar_factura_final():
    global carrito_actual
    cliente = combo_fac_cliente.get()
    
    if not cliente:
        messagebox.showwarning("Aviso", "Seleccione un cliente.")
        return
    if len(carrito_actual) == 0:
        messagebox.showwarning("Aviso", "El carrito está vacío.")
        return
        
    try:
        documento_cliente = cliente.split(" - ")[0] 
        
        # 1. Guardar en la base de datos
        backend.procesar_factura_completa(documento_cliente, carrito_actual)
        
        # 2. Llamar a WhatsApp (¡El código que se me había pasado!)
        total_factura = sum(item['venta_total'] for item in carrito_actual)
        try:
            backend.enviar_factura_whatsapp(documento_cliente, carrito_actual, total_factura)
        except Exception as e:
            print(f"No se pudo abrir WhatsApp: {e}")
            
        messagebox.showinfo("Éxito", "Factura Generada Correctamente.")
        
        # 3. Limpiar todo
        carrito_actual = []
        for fila in tabla_factura.get_children(): tabla_factura.delete(fila)
        lbl_total_factura.config(text="TOTAL: $0")
        combo_fac_cliente.set('')
        recargar_inventario() 
        recargar_historial_facturas() 
        
    except ValueError as e:
        messagebox.showwarning("Error", str(e))

# ==========================================
# NUEVAS FUNCIONES: HISTORIAL DE FACTURAS
# ==========================================
def recargar_historial_facturas():
    for fila in tabla_historial.get_children(): 
        tabla_historial.delete(fila)
    try:
        # Obtenemos las facturas y usamos 'reversed' para que la más nueva salga arriba
        facturas = backend.obtener_facturas()
        for f in reversed(facturas):
            tabla_historial.insert("", "end", values=(f["fecha"], f["cliente_nombre"], f"${f['total_venta']:,}"))
    except: pass

def accion_exportar_factura():
    seleccion = tabla_historial.selection()
    if not seleccion:
        messagebox.showwarning("Aviso", "Debes seleccionar una factura de la lista.")
        return
    item = tabla_historial.item(seleccion[0])
    fecha_id = item["values"][0] # Extraemos la fecha que sirve como ID
    
    try:
        backend.exportar_factura_txt(fecha_id)
        # No mostramos popup porque el Bloc de Notas se abrirá automáticamente
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def accion_anular_factura():
    seleccion = tabla_historial.selection()
    if not seleccion:
        messagebox.showwarning("Aviso", "Debes seleccionar una factura para anular.")
        return
    item = tabla_historial.item(seleccion[0])
    fecha_id = item["values"][0]
    
    # Preguntamos por seguridad antes de borrar
    respuesta = messagebox.askyesno("Anular Factura", f"¿Estás seguro de anular la factura del {fecha_id}?\n\nLos productos vendidos regresarán a la bodega de inventario.")
    
    if respuesta:
        try:
            backend.anular_factura(fecha_id)
            messagebox.showinfo("Anulada", "La factura ha sido borrada y el stock fue recuperado.")
            recargar_historial_facturas()
            recargar_inventario() # Actualizamos la vista de la bodega
        except ValueError as e:
            messagebox.showerror("Error", str(e))

# ==========================================
# INTERFAZ GRÁFICA PRINCIPAL
# ==========================================
ventana = tk.Tk()
ventana.title("Sistema POS Integral - Helados")
ventana.geometry("850x700")

notebook = ttk.Notebook(ventana)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

pestaña_ventas = ttk.Frame(notebook)
pestaña_facturacion = ttk.Frame(notebook)
pestaña_clientes = ttk.Frame(notebook)
pestaña_inventario = ttk.Frame(notebook)
pestaña_historial = ttk.Frame(notebook) # LA NUEVA PESTAÑA

notebook.add(pestaña_ventas, text="🛒 Venta Rápida")
notebook.add(pestaña_facturacion, text="🧾 Facturación Detallada")
notebook.add(pestaña_historial, text="📂 Historial de Facturas") # NUEVO
notebook.add(pestaña_clientes, text="👥 Clientes")
notebook.add(pestaña_inventario, text="📦 Inventario")

try: lista_sabores = backend.obtener_lista_sabores()
except: lista_sabores = []

# --- PESTAÑA 1: VENTA RÁPIDA ---
marco_form_v = tk.LabelFrame(pestaña_ventas, text="Venta Anónima", padx=10, pady=10); marco_form_v.pack(fill="x", padx=10, pady=10)
tk.Label(marco_form_v, text="Sabor:").grid(row=0, column=0); combo_ventas_sabores = ttk.Combobox(marco_form_v, values=lista_sabores, state="readonly"); combo_ventas_sabores.grid(row=0, column=1)
tk.Label(marco_form_v, text="Cant:").grid(row=1, column=0); entrada_ventas_cantidad = ttk.Entry(marco_form_v); entrada_ventas_cantidad.grid(row=1, column=1)
tk.Button(marco_form_v, text="Registrar", command=registrar_venta_rapida).grid(row=2, column=0, columnspan=2, pady=5)
marco_tabla_v = tk.LabelFrame(pestaña_ventas, text="Ventas Rápidas del Día"); marco_tabla_v.pack(fill="both", expand=True, padx=10)
tabla_ventas = ttk.Treeview(marco_tabla_v, columns=("sabor", "cantidad", "costo", "venta"), show="headings")
tabla_ventas.heading("sabor", text="Sabor"); tabla_ventas.heading("cantidad", text="Cant."); tabla_ventas.heading("costo", text="Costo"); tabla_ventas.heading("venta", text="Venta")
tabla_ventas.pack(fill="both", expand=True)
marco_totales = tk.Frame(pestaña_ventas); marco_totales.pack(fill="x", padx=10, pady=10)
lbl_total_costo = tk.Label(marco_totales, text="Costo: $0"); lbl_total_costo.pack(anchor="e")
lbl_total_ventas = tk.Label(marco_totales, text="Ingresos: $0"); lbl_total_ventas.pack(anchor="e")
lbl_total_ganancia = tk.Label(marco_totales, text="Ganancia: $0"); lbl_total_ganancia.pack(anchor="e")

# --- PESTAÑA 2: FACTURACIÓN ---
marco_form_f = tk.LabelFrame(pestaña_facturacion, text="Armar Pedido", padx=10, pady=10); marco_form_f.pack(fill="x", padx=10, pady=10)
tk.Label(marco_form_f, text="Cliente:").grid(row=0, column=0, sticky="w"); combo_fac_cliente = ttk.Combobox(marco_form_f, width=40, state="readonly"); combo_fac_cliente.grid(row=0, column=1, columnspan=2, pady=5)
tk.Label(marco_form_f, text="Producto:").grid(row=1, column=0, sticky="w"); combo_fac_sabores = ttk.Combobox(marco_form_f, values=lista_sabores, width=20, state="readonly"); combo_fac_sabores.grid(row=1, column=1, pady=5)
tk.Label(marco_form_f, text="Cant:").grid(row=1, column=2, sticky="e"); entrada_fac_cantidad = ttk.Entry(marco_form_f, width=10); entrada_fac_cantidad.grid(row=1, column=3, pady=5, padx=5)
tk.Button(marco_form_f, text="Añadir al Carrito ⬇", command=agregar_al_carrito).grid(row=2, column=0, columnspan=4, pady=10)
marco_tabla_f = tk.LabelFrame(pestaña_facturacion, text="Carrito de Compras", padx=10, pady=10); marco_tabla_f.pack(fill="both", expand=True, padx=10)
tabla_factura = ttk.Treeview(marco_tabla_f, columns=("sabor", "cant", "subtotal"), show="headings", height=6)
tabla_factura.heading("sabor", text="Producto"); tabla_factura.heading("cant", text="Cantidad"); tabla_factura.heading("subtotal", text="Subtotal")
tabla_factura.pack(fill="both", expand=True)
marco_cierre = tk.Frame(pestaña_facturacion); marco_cierre.pack(fill="x", padx=10, pady=10)
lbl_total_factura = tk.Label(marco_cierre, text="TOTAL: $0", font=("Arial", 16, "bold"), fg="#D32F2F"); lbl_total_factura.pack(side="left")
tk.Button(marco_cierre, text="💰 GENERAR FACTURA", bg="#1976D2", fg="white", font=("Arial", 10, "bold"), command=generar_factura_final).pack(side="right", ipadx=10, ipady=5)

# --- PESTAÑA 3: HISTORIAL DE FACTURAS (¡NUEVA!) ---
marco_tabla_h = tk.LabelFrame(pestaña_historial, text="Todas las Ventas Registradas", padx=10, pady=10)
marco_tabla_h.pack(fill="both", expand=True, padx=10, pady=10)

tabla_historial = ttk.Treeview(marco_tabla_h, columns=("fecha", "cliente", "total"), show="headings", height=15)
tabla_historial.heading("fecha", text="Fecha Exacta (ID)")
tabla_historial.heading("cliente", text="Cliente")
tabla_historial.heading("total", text="Total Facturado")
tabla_historial.column("fecha", width=200)
tabla_historial.column("cliente", width=200)
tabla_historial.column("total", width=100, anchor="e")
tabla_historial.pack(fill="both", expand=True)

marco_botones_h = tk.Frame(pestaña_historial)
marco_botones_h.pack(fill="x", padx=10, pady=10)
tk.Button(marco_botones_h, text="📄 Exportar/Descargar Recibo", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=accion_exportar_factura).pack(side="left", padx=5, ipadx=10)
tk.Button(marco_botones_h, text="❌ Anular Venta y Devolver Stock", bg="#D32F2F", fg="white", font=("Arial", 10, "bold"), command=accion_anular_factura).pack(side="right", padx=5, ipadx=10)

# --- PESTAÑA 4: CLIENTES ---
marco_form_c = tk.LabelFrame(pestaña_clientes, text="Nuevo Cliente", padx=10, pady=10); marco_form_c.pack(fill="x", padx=10, pady=10)
tk.Label(marco_form_c, text="Doc/NIT:").grid(row=0, column=0, sticky="w"); entrada_cli_doc = ttk.Entry(marco_form_c, width=30); entrada_cli_doc.grid(row=0, column=1)
tk.Label(marco_form_c, text="Nombre:").grid(row=1, column=0, sticky="w"); entrada_cli_nom = ttk.Entry(marco_form_c, width=30); entrada_cli_nom.grid(row=1, column=1)
tk.Label(marco_form_c, text="Teléfono:").grid(row=2, column=0, sticky="w"); entrada_cli_tel = ttk.Entry(marco_form_c, width=30); entrada_cli_tel.grid(row=2, column=1)
tk.Button(marco_form_c, text="Guardar Cliente", command=guardar_nuevo_cliente).grid(row=3, column=0, columnspan=2, pady=10)
marco_tabla_c = tk.LabelFrame(pestaña_clientes, text="Directorio"); marco_tabla_c.pack(fill="both", expand=True, padx=10)
tabla_clientes = ttk.Treeview(marco_tabla_c, columns=("doc", "nom", "tel"), show="headings")
tabla_clientes.heading("doc", text="Doc"); tabla_clientes.heading("nom", text="Nombre"); tabla_clientes.heading("tel", text="Teléfono")
tabla_clientes.pack(fill="both", expand=True)

# --- PESTAÑA 5: INVENTARIO ---
marco_form_i = tk.LabelFrame(pestaña_inventario, text="Ingreso Bodega", padx=10, pady=10); marco_form_i.pack(fill="x", padx=10, pady=10)
tk.Label(marco_form_i, text="Sabor:").grid(row=0, column=0); combo_inv_sabores = ttk.Combobox(marco_form_i, values=lista_sabores, state="readonly"); combo_inv_sabores.grid(row=0, column=1)
tk.Label(marco_form_i, text="Cant:").grid(row=1, column=0); entrada_inv_cantidad = ttk.Entry(marco_form_i); entrada_inv_cantidad.grid(row=1, column=1)
tk.Button(marco_form_i, text="Actualizar", command=guardar_ingreso).grid(row=2, column=0, columnspan=2, pady=5)
marco_tabla_i = tk.LabelFrame(pestaña_inventario, text="Stock Actual"); marco_tabla_i.pack(fill="both", expand=True, padx=10)
tabla_inventario = ttk.Treeview(marco_tabla_i, columns=("sabor", "stock"), show="headings")
tabla_inventario.heading("sabor", text="Sabor"); tabla_inventario.heading("stock", text="Unidades")
tabla_inventario.pack(fill="both", expand=True)

# --- BOTÓN INFERIOR (DASHBOARD WEB) ---
tk.Button(ventana, text="📊 ABRIR DASHBOARD ANALÍTICO WEB", bg="#673AB7", fg="white", font=("Arial", 12, "bold"), command=backend.lanzar_dashboard).pack(fill="x", padx=10, pady=10, side="bottom")

# Inicializar todo al arrancar
recargar_inventario()
recargar_clientes()
recargar_historial_facturas()

ventana.mainloop()