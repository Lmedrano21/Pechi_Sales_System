import tkinter as tk
from tkinter import ttk, messagebox
import backend

class HeladeriaApp:
    # --- PALETA DE COLORES CÁLIDA (SOFT & LIGHT) ---
    COLOR_FONDO = "#FFF9F0"  # Crema muy suave
    COLOR_PRIMARIO = "#D35400"  # Naranja Tierra (Tostado)
    COLOR_ACCION = "#E67E22"  # Melocotón oscuro (Cálido)
    COLOR_TABLAS = "#FFFFFF"
    COLOR_TEXTO = "#3E2723"  # Café oscuro (Suave)
    COLOR_BORDE = "#FAD7A0"  # Arena claro

    def __init__(self, root):
        self.root = root
        self.root.title("Antigravity - Sistema de Ventas")
        self.root.geometry("1100x750")
        self.root.configure(bg=self.COLOR_FONDO)
        
        # Estado de la aplicación
        self.acumulado_costo = 0.0
        self.acumulado_ventas = 0.0
        self.acumulado_ganancia = 0.0
        self.carrito_actual = []
        
        self.configurar_estilos()
        self.setup_ui()
        self.inicializar_datos()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')  # Base moderna

        # Notebook (Pestañas)
        style.configure("TNotebook", background=self.COLOR_FONDO, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.COLOR_BORDE, padding=[20, 8], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", self.COLOR_PRIMARIO)], foreground=[("selected", "white")])

        # Botones Modernos
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("Accion.TButton", background=self.COLOR_ACCION, foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Accion.TButton", background=[("active", "#219150")])

        # Treeview (Tablas)
        style.configure("Treeview", 
                        background=self.COLOR_TABLAS, 
                        foreground=self.COLOR_TEXTO, 
                        fieldbackground=self.COLOR_TABLAS, 
                        rowheight=35,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=self.COLOR_PRIMARIO, foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", self.COLOR_ACCION)], foreground=[("selected", "white")])

        # Frames y Labels
        style.configure("TFrame", background=self.COLOR_FONDO)
        style.configure("TLabel", background=self.COLOR_FONDO, foreground=self.COLOR_TEXTO, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=self.COLOR_PRIMARIO, foreground="white", font=("Segoe UI", 16, "bold"))

    def setup_ui(self):
        # Header Superior
        header = tk.Frame(self.root, bg=self.COLOR_PRIMARIO, height=60)
        header.pack(fill="x")
        tk.Label(header, text="SISTEMA DE VENTAS", bg=self.COLOR_PRIMARIO, fg="white", font=("Segoe UI", 18, "bold")).pack(side="left", padx=20, pady=10)
        tk.Label(header, text="POS System v2.0", bg=self.COLOR_PRIMARIO, fg="#FAD7A0", font=("Segoe UI", 10)).pack(side="left", pady=(15,0))
        
        btn_dash = tk.Button(header, text="🌐 Dashboard Web", command=self.abrir_dashboard, bg="#E67E22", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=15)
        btn_dash.pack(side="right", padx=20)

        # Contenedor de Pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Pestañas
        self.pestana_ventas = ttk.Frame(self.notebook)
        self.pestana_facturacion = ttk.Frame(self.notebook)
        self.pestana_historial = ttk.Frame(self.notebook)
        self.pestana_clientes = ttk.Frame(self.notebook)
        self.pestana_inventario = ttk.Frame(self.notebook)

        self.notebook.add(self.pestana_ventas, text="🛒 Venta Rápida")
        self.notebook.add(self.pestana_facturacion, text="🧾 Facturación Detallada")
        self.notebook.add(self.pestana_historial, text="📂 Historial")
        self.notebook.add(self.pestana_clientes, text="👥 Clientes")
        self.notebook.add(self.pestana_inventario, text="📦 Inventario")

        self.setup_pestana_ventas()
        self.setup_pestana_facturacion()
        self.setup_pestana_historial()
        self.setup_pestana_clientes()
        self.setup_pestana_inventario()

        # Botón Dashboard
        tk.Button(self.root, text="📊 ABRIR DASHBOARD ANALÍTICO WEB", bg=self.COLOR_PRIMARIO, fg="white", 
                  font=("Arial", 12, "bold"), command=backend.lanzar_dashboard).pack(fill="x", padx=10, pady=10)

    def setup_pestana_ventas(self):
        # Formulario
        marco = tk.LabelFrame(self.pestana_ventas, text="Nueva Venta Rápida", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=10)
        
        # Split Layout: Izquierda (Búsqueda) | Derecha (Entradas)
        f_izq = tk.Frame(marco); f_izq.pack(side="left", fill="both", expand=True)
        f_der = tk.Frame(marco, padx=20); f_der.pack(side="right", fill="both")

        # Izquierda
        tk.Label(f_izq, text="🔍 Buscar Producto:").pack(anchor="w")
        self.ent_v_buscar = ttk.Entry(f_izq)
        self.ent_v_buscar.pack(fill="x", pady=2)
        self.ent_v_buscar.bind("<KeyRelease>", lambda e: self.filtrar_listbox(e, self.ent_v_buscar, self.list_v_sabores, self.sabores_lista))
        
        f_lista = tk.Frame(f_izq)
        f_lista.pack(fill="both", expand=True)
        self.list_v_sabores = tk.Listbox(f_lista, height=5, exportselection=False, font=("Arial", 10))
        self.list_v_sabores.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(f_lista, orient="vertical", command=self.list_v_sabores.yview)
        scroll.pack(side="right", fill="y")
        self.list_v_sabores.config(yscrollcommand=scroll.set)

        # Derecha
        tk.Label(f_der, text="Cantidad:").pack(anchor="w")
        self.ent_v_cantidad = ttk.Entry(f_der, width=15)
        self.ent_v_cantidad.pack(pady=2)
        
        tk.Label(f_der, text="Método Pago:").pack(anchor="w", pady=(5,0))
        self.combo_v_pago = ttk.Combobox(f_der, values=["Efectivo", "Transferencia", "Tarjeta"], state="readonly", width=13)
        self.combo_v_pago.set("Efectivo")
        self.combo_v_pago.pack(pady=2)
        
        tk.Button(f_der, text="✅ REGISTRAR", command=self.registrar_venta_rapida, 
                  bg=self.COLOR_ACCION, fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(pady=10)

        # Tabla
        self.tabla_ventas = ttk.Treeview(self.pestana_ventas, columns=("sabor", "cant", "costo", "venta"), show="headings")
        for col, head in zip(self.tabla_ventas["columns"], ("Sabor", "Cant.", "Costo", "Venta")):
            self.tabla_ventas.heading(col, text=head)
        self.tabla_ventas.pack(fill="both", expand=True, padx=10)

        # Totales
        self.lbl_v_costo = tk.Label(self.pestana_ventas, text="Costo: $0", anchor="e")
        self.lbl_v_costo.pack(fill="x", padx=20)
        self.lbl_v_ingresos = tk.Label(self.pestana_ventas, text="Ingresos: $0", anchor="e")
        self.lbl_v_ingresos.pack(fill="x", padx=20)
        self.lbl_v_ganancia = tk.Label(self.pestana_ventas, text="Ganancia: $0", anchor="e", font=("Arial", 10, "bold"))
        self.lbl_v_ganancia.pack(fill="x", padx=20)

    def setup_pestana_facturacion(self):
        marco = tk.LabelFrame(self.pestana_facturacion, text="Armar Pedido Detallado", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=5)

        # Arriba: Selección de Cliente y Pago
        f_top = tk.Frame(marco); f_top.pack(fill="x", pady=5)
        tk.Label(f_top, text="👤 Cliente:").pack(side="left")
        self.combo_f_cliente = ttk.Combobox(f_top, width=35, state="readonly")
        self.combo_f_cliente.pack(side="left", padx=5)
        
        tk.Label(f_top, text="💳 Pago:").pack(side="left", padx=(15,0))
        self.combo_f_pago = ttk.Combobox(f_top, values=["Efectivo", "Transferencia", "Tarjeta"], state="readonly", width=12)
        self.combo_f_pago.set("Efectivo"); self.combo_f_pago.pack(side="left", padx=5)

        # Abajo: Búsqueda y Añadir
        f_bot = tk.Frame(marco); f_bot.pack(fill="x", pady=5)
        f_izq = tk.Frame(f_bot); f_izq.pack(side="left", fill="both", expand=True)
        f_der = tk.Frame(f_bot, padx=20); f_der.pack(side="right", fill="both")

        tk.Label(f_izq, text="🔍 Buscar Producto:").pack(anchor="w")
        self.ent_f_buscar = ttk.Entry(f_izq)
        self.ent_f_buscar.pack(fill="x", pady=2)
        self.ent_f_buscar.bind("<KeyRelease>", lambda e: self.filtrar_listbox(e, self.ent_f_buscar, self.list_f_sabores, self.sabores_lista))

        f_lista = tk.Frame(f_izq)
        f_lista.pack(fill="both", expand=True)
        self.list_f_sabores = tk.Listbox(f_lista, height=4, exportselection=False, font=("Arial", 9))
        self.list_f_sabores.pack(side="left", fill="both", expand=True)
        scroll_f = ttk.Scrollbar(f_lista, orient="vertical", command=self.list_f_sabores.yview)
        scroll_f.pack(side="right", fill="y")
        self.list_f_sabores.config(yscrollcommand=scroll_f.set)

        tk.Label(f_der, text="Cant:").pack(anchor="w")
        self.ent_f_cantidad = ttk.Entry(f_der, width=10)
        self.ent_f_cantidad.pack(pady=2)
        
        tk.Button(f_der, text="➕ Añadir", command=self.agregar_al_carrito, 
                  bg=self.COLOR_ACCION, fg="white", font=("Arial", 9, "bold"), width=12).pack(pady=5)

        self.tabla_f_carrito = ttk.Treeview(self.pestana_facturacion, columns=("sabor", "cant", "subtotal"), show="headings", height=8)
        for col, head in zip(self.tabla_f_carrito["columns"], ("Producto", "Cantidad", "Subtotal")):
            self.tabla_f_carrito.heading(col, text=head)
        self.tabla_f_carrito.pack(fill="both", expand=True, padx=10)

        marco_cierre = tk.Frame(self.pestana_facturacion)
        marco_cierre.pack(fill="x", padx=10, pady=10)
        self.lbl_f_total = tk.Label(marco_cierre, text="TOTAL: $0", font=("Arial", 14, "bold"), fg="black")
        self.lbl_f_total.pack(side="left")
        tk.Button(marco_cierre, text="💰 GENERAR FACTURA & WHATSAPP", bg=self.COLOR_PRIMARIO, fg="white", 
                  font=("Arial", 10, "bold"), command=self.generar_factura_final).pack(side="right", padx=10)

    def setup_pestana_historial(self):
        self.tabla_h = ttk.Treeview(self.pestana_historial, columns=("fecha", "cliente", "total"), show="headings")
        for col, head in zip(self.tabla_h["columns"], ("Fecha/ID", "Cliente", "Total")):
            self.tabla_h.heading(col, text=head)
        self.tabla_h.pack(fill="both", expand=True, padx=10, pady=10)

        marco_btn = tk.Frame(self.pestana_historial)
        marco_btn.pack(fill="x", padx=10, pady=5)
        tk.Button(marco_btn, text="📄 Exportar TXT", bg="#4CAF50", fg="white", command=self.exportar_txt).pack(side="left", padx=5)
        tk.Button(marco_btn, text="❌ Anular Venta", bg="#F44336", fg="white", command=self.anular_venta).pack(side="right", padx=5)

    def setup_pestana_clientes(self):
        marco = tk.LabelFrame(self.pestana_clientes, text="Gestión de Clientes", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=10)

        tk.Label(marco, text="Documento:").grid(row=0, column=0, sticky="w")
        self.ent_c_doc = ttk.Entry(marco); self.ent_c_doc.grid(row=0, column=1)
        tk.Label(marco, text="Nombre:").grid(row=1, column=0, sticky="w")
        self.ent_c_nom = ttk.Entry(marco); self.ent_c_nom.grid(row=1, column=1)
        tk.Label(marco, text="Teléfono:").grid(row=2, column=0, sticky="w")
        self.ent_c_tel = ttk.Entry(marco); self.ent_c_tel.grid(row=2, column=1)
        tk.Label(marco, text="Dirección:").grid(row=3, column=0, sticky="w")
        self.ent_c_dir = ttk.Entry(marco); self.ent_c_dir.grid(row=3, column=1)
        tk.Button(marco, text="Registrar Cliente", command=self.registrar_cliente).grid(row=4, column=0, columnspan=2, pady=10)

        self.tabla_clientes = ttk.Treeview(self.pestana_clientes, columns=("doc", "nom", "tel", "dir"), show="headings")
        for col, head in zip(self.tabla_clientes["columns"], ("Documento", "Nombre", "Teléfono", "Dirección")):
            self.tabla_clientes.heading(col, text=head)
        self.tabla_clientes.pack(fill="both", expand=True, padx=10)

        marco_btn = tk.Frame(self.pestana_clientes)
        marco_btn.pack(fill="x", padx=10, pady=10)
        tk.Button(marco_btn, text="✏️ Editar", command=self.editar_cliente).pack(side="left", padx=5)
        tk.Button(marco_btn, text="🗑️ Eliminar", command=self.eliminar_cliente).pack(side="left", padx=5)

    def setup_pestana_inventario(self):
        # Marco para Ajuste de Stock
        marco_stock = tk.LabelFrame(self.pestana_inventario, text="Ajuste Rápido de Stock", padx=10, pady=10)
        marco_stock.pack(fill="x", padx=10, pady=5)
        
        tk.Label(marco_stock, text="Producto:").grid(row=0, column=0)
        self.combo_i_sabor = ttk.Combobox(marco_stock, state="normal")
        self.combo_i_sabor.grid(row=0, column=1, padx=5)
        self.combo_i_sabor.bind("<KeyRelease>", lambda e: self.filtrar_combo(e, self.combo_i_sabor, self.sabores_lista))
        
        tk.Label(marco_stock, text="Cantidad:").grid(row=0, column=2)
        self.ent_i_cantidad = ttk.Entry(marco_stock, width=10)
        self.ent_i_cantidad.grid(row=0, column=3, padx=5)
        
        tk.Button(marco_stock, text="➕ Sumar", command=self.actualizar_stock, bg="#FFEB3B").grid(row=0, column=4, padx=5)
        tk.Button(marco_stock, text="🎯 Fijar", command=self.fijar_stock, bg="#FF9800").grid(row=0, column=5, padx=5)

        # Marco para Gestión de Productos
        marco_crud = tk.LabelFrame(self.pestana_inventario, text="Gestión de Catálogo (Nuevo/Editar)", padx=10, pady=10)
        marco_crud.pack(fill="x", padx=10, pady=5)

        tk.Button(marco_crud, text="✨ NUEVO PRODUCTO", command=self.abrir_ventana_nuevo_producto, bg=self.COLOR_ACCION, fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(marco_crud, text="✏️ Editar Precios", command=self.abrir_ventana_editar_producto, bg="white", fg=self.COLOR_TEXTO).pack(side="left", padx=5)
        tk.Button(marco_crud, text="🗑️ Eliminar Sabor", command=self.eliminar_sabor, bg="#A04000", fg="white").pack(side="right", padx=5)

        # Tabla de Inventario Completa
        self.tabla_inv = ttk.Treeview(self.pestana_inventario, columns=("sabor", "costo", "precio", "stock"), show="headings")
        self.tabla_inv.heading("sabor", text="Sabor")
        self.tabla_inv.heading("costo", text="Costo")
        self.tabla_inv.heading("precio", text="P. Venta")
        self.tabla_inv.heading("stock", text="Stock")
        self.tabla_inv.pack(fill="both", expand=True, padx=10, pady=5)

    # --- LÓGICA ---
    def inicializar_datos(self):
        self.recargar_todo()

    def recargar_todo(self):
        self.sabores_lista = backend.obtener_lista_sabores()
        # Actualizar listboxes
        for lb in [self.list_v_sabores, self.list_f_sabores]:
            lb.delete(0, tk.END)
            for s in self.sabores_lista: lb.insert(tk.END, s)
        
        # Mantener el combo de inventario igual o actualizarlo
        self.combo_i_sabor.config(values=self.sabores_lista)
        
        self.recargar_inventario()
        self.recargar_clientes()
        self.recargar_historial()

    def recargar_inventario(self):
        for f in self.tabla_inv.get_children(): self.tabla_inv.delete(f)
        for sabor, data in backend.obtener_inventario().items():
            self.tabla_inv.insert("", "end", values=(sabor, f"${data['costo']:,}", f"${data['precio']:,}", data.get('stock', 0)))

    def abrir_dashboard(self):
        backend.lanzar_dashboard()
        import webbrowser
        webbrowser.open("http://localhost:8000")

    def recargar_clientes(self):
        for f in self.tabla_clientes.get_children(): self.tabla_clientes.delete(f)
        clientes = backend.obtener_clientes()
        for doc, data in clientes.items():
            self.tabla_clientes.insert("", "end", values=(doc, data['nombre'], data['telefono'], data.get('direccion', 'N/A')))
        self.combo_f_cliente.config(values=[f"{doc} - {data['nombre']}" for doc, data in clientes.items()])

    def recargar_historial(self):
        for f in self.tabla_h.get_children(): self.tabla_h.delete(f)
        facturas = backend.obtener_facturas()
        for f in reversed(facturas):
            self.tabla_h.insert("", "end", values=(f["fecha"], f["cliente_nombre"], f"${f['total_venta']:,}"))

    def registrar_venta_rapida(self):
        seleccion = self.list_v_sabores.curselection()
        if not seleccion: return messagebox.showwarning("Aviso", "Seleccione un sabor de la lista.")
        sabor = self.list_v_sabores.get(seleccion[0])
        cant = self.ent_v_cantidad.get()
        pago = self.combo_v_pago.get()  # <-- Nuevo
        try:
            v = backend.procesar_venta(sabor, cant, pago)  # <-- Enviamos pago
            self.tabla_ventas.insert("", 0, values=(v['sabor'], v['cantidad'], f"${v['costo_total']:,}", f"${v['venta_total']:,}"))
            self.acumulado_costo += v['costo_total']
            self.acumulado_ventas += v['venta_total']
            self.acumulado_ganancia += v['ganancia']
            self.lbl_v_costo.config(text=f"Costo: ${self.acumulado_costo:,.0f}")
            self.lbl_v_ingresos.config(text=f"Ingresos: ${self.acumulado_ventas:,.0f}")
            self.lbl_v_ganancia.config(text=f"Ganancia: ${self.acumulado_ganancia:,.0f}")
            self.ent_v_buscar.delete(0, tk.END)
            self.ent_v_cantidad.delete(0, tk.END)
            self.recargar_todo()
        except ValueError as e: messagebox.showwarning("Error", str(e))

    def agregar_al_carrito(self):
        seleccion = self.list_f_sabores.curselection()
        if not seleccion: return messagebox.showwarning("Aviso", "Seleccione un producto de la lista.")
        sabor = self.list_f_sabores.get(seleccion[0])
        cant = self.ent_f_cantidad.get()
        try:
            item = backend.cotizar_item(sabor, cant)
            self.carrito_actual.append(item)
            self.tabla_f_carrito.insert("", "end", values=(item['sabor'], item['cantidad'], f"${item['venta_total']:,}"))
            total = sum(x['venta_total'] for x in self.carrito_actual)
            self.lbl_f_total.config(text=f"TOTAL: ${total:,.0f}")
            self.ent_f_buscar.delete(0, tk.END)
            self.ent_f_cantidad.delete(0, tk.END)
            self.recargar_todo()
        except ValueError as e: messagebox.showwarning("Error", str(e))

    def generar_factura_final(self):
        cliente_str = self.combo_f_cliente.get()
        pago = self.combo_f_pago.get()  # <-- Nuevo
        if not cliente_str or not self.carrito_actual:
            return messagebox.showwarning("Aviso", "Seleccione cliente y productos.")
        
        try:
            doc = cliente_str.split(" - ")[0]
            backend.procesar_factura_completa(doc, self.carrito_actual, pago) # <-- Enviamos pago
            total = sum(i['venta_total'] for i in self.carrito_actual)
            try: backend.enviar_factura_whatsapp(doc, self.carrito_actual, total)
            except: pass
            
            messagebox.showinfo("Éxito", "Factura generada correctamente.")
            self.carrito_actual = []
            for f in self.tabla_f_carrito.get_children(): self.tabla_f_carrito.delete(f)
            self.lbl_f_total.config(text="TOTAL: $0")
            self.combo_f_cliente.set('')
            self.recargar_todo()
        except ValueError as e: messagebox.showwarning("Error", str(e))

    def registrar_cliente(self):
        doc, nom, tel, dir_ = self.ent_c_doc.get(), self.ent_c_nom.get(), self.ent_c_tel.get(), self.ent_c_dir.get()
        try:
            backend.registrar_cliente(doc, nom, tel, dir_)
            messagebox.showinfo("Éxito", "Cliente registrado.")
            for ent in [self.ent_c_doc, self.ent_c_nom, self.ent_c_tel, self.ent_c_dir]: ent.delete(0, tk.END)
            self.recargar_clientes()
        except ValueError as e: messagebox.showwarning("Error", str(e))

    def editar_cliente(self):
        sel = self.tabla_clientes.selection()
        if not sel: return messagebox.showwarning("Aviso", "Seleccione un cliente.")
        item = self.tabla_clientes.item(sel[0])["values"]
        
        # Ventana simple de edición
        win = tk.Toplevel(self.root)
        win.title("Editar Cliente")
        tk.Label(win, text=f"Editando Doc: {item[0]}").pack(pady=5)
        tk.Label(win, text="Nombre:").pack()
        en = ttk.Entry(win); en.insert(0, item[1]); en.pack()
        tk.Label(win, text="Tel:").pack()
        et = ttk.Entry(win); et.insert(0, item[2]); et.pack()
        tk.Label(win, text="Dir:").pack()
        ed = ttk.Entry(win); ed.insert(0, item[3] if len(item)>3 else ""); ed.pack()
        
        def save():
            try:
                backend.editar_cliente(str(item[0]), en.get(), et.get(), ed.get())
                self.recargar_clientes(); win.destroy()
            except ValueError as e: messagebox.showwarning("Error", str(e))
        tk.Button(win, text="Guardar", command=save).pack(pady=10)

    def eliminar_cliente(self):
        sel = self.tabla_clientes.selection()
        if not sel: return
        doc = self.tabla_clientes.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar cliente {doc}?"):
            try: backend.eliminar_cliente(str(doc)); self.recargar_clientes()
            except ValueError as e: messagebox.showwarning("Error", str(e))

    def actualizar_stock(self):
        sabor = self.combo_i_sabor.get()
        cant = self.ent_i_cantidad.get()
        try:
            backend.actualizar_stock(sabor, cant)
            messagebox.showinfo("Éxito", f"Se sumó {cant} unidades al stock de {sabor}.")
            self.combo_i_sabor.set(''); self.ent_i_cantidad.delete(0, tk.END)
            self.recargar_inventario()
        except ValueError as e: messagebox.showwarning("Error", str(e))

    def fijar_stock(self):
        sabor = self.combo_i_sabor.get()
        cant = self.ent_i_cantidad.get()
        try:
            backend.fijar_stock(sabor, cant)
            messagebox.showinfo("Éxito", f"Se estableció el stock de {sabor} en {cant} unidades.")
            self.combo_i_sabor.set(''); self.ent_i_cantidad.delete(0, tk.END)
            self.recargar_inventario()
        except ValueError as e: messagebox.showwarning("Error", str(e))

    def anular_venta(self):
        sel = self.tabla_h.selection()
        if not sel: return
        fid = self.tabla_h.item(sel[0])["values"][0]
        if messagebox.askyesno("Anular", f"¿Anular factura {fid}?"):
            try: backend.anular_factura(fid); self.recargar_todo()
            except ValueError as e: messagebox.showwarning("Error", str(e))

    def exportar_txt(self):
        sel = self.tabla_h.selection()
        if not sel: return
        try:
            backend.exportar_factura_txt(self.tabla_h.item(sel[0])["values"][0])
        except ValueError as e: messagebox.showwarning("Error", str(e))

    def abrir_ventana_nuevo_producto(self):
        win = tk.Toplevel(self.root); win.title("Nuevo Producto")
        tk.Label(win, text="Sabor:").pack(); e_sab = ttk.Entry(win); e_sab.pack()
        tk.Label(win, text="Costo:").pack(); e_cos = ttk.Entry(win); e_cos.pack()
        tk.Label(win, text="Precio Venta:").pack(); e_pre = ttk.Entry(win); e_pre.pack()
        tk.Label(win, text="Stock Inicial:").pack(); e_stk = ttk.Entry(win); e_stk.pack()
        
        def save():
            try:
                backend.registrar_producto(e_sab.get(), e_cos.get(), e_pre.get(), e_stk.get())
                self.recargar_todo(); win.destroy()
            except ValueError as e: messagebox.showwarning("Error", str(e))
        tk.Button(win, text="Guardar", command=save, bg=self.COLOR_ACCION, fg="white").pack(pady=10)

    def abrir_ventana_editar_producto(self):
        sel = self.tabla_inv.selection()
        if not sel: return messagebox.showwarning("Aviso", "Seleccione un producto.")
        item = self.tabla_inv.item(sel[0])["values"]
        
        win = tk.Toplevel(self.root); win.title("Editar Producto")
        tk.Label(win, text="Nombre Sabor:").pack(); e_sab = ttk.Entry(win); e_sab.insert(0, item[0]); e_sab.pack()
        tk.Label(win, text="Costo:").pack(); e_cos = ttk.Entry(win); e_cos.insert(0, item[1].replace("$","").replace(",","")); e_cos.pack()
        tk.Label(win, text="Precio Venta:").pack(); e_pre = ttk.Entry(win); e_pre.insert(0, item[2].replace("$","").replace(",","")); e_pre.pack()
        
        def save():
            try:
                backend.editar_producto(str(item[0]), e_sab.get(), e_cos.get(), e_pre.get())
                self.recargar_todo(); win.destroy()
            except ValueError as e: messagebox.showwarning("Error", str(e))
        tk.Button(win, text="Guardar Cambios", command=save, bg=self.COLOR_ACCION, fg="white").pack(pady=10)

    def eliminar_sabor(self):
        sel = self.tabla_inv.selection()
        if not sel: return
        sabor = self.tabla_inv.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar {sabor} del catálogo?"):
            try:
                backend.eliminar_producto(str(sabor))
                self.recargar_todo()
            except ValueError as e: messagebox.showwarning("Error", str(e))

    def filtrar_combo(self, event, combo, lista_completa):
        """Filtra los valores del combobox según lo que el usuario escribe."""
        val = event.widget.get().lower()
        if val == '':
            combo['values'] = lista_completa
        else:
            filtrados = [x for x in lista_completa if val in x.lower()]
            combo['values'] = filtrados
        
        # Abrir el desplegable si hay coincidencias
        if combo['values']:
            combo.event_generate('<Down>')

    def filtrar_listbox(self, event, entry, listbox, lista_completa):
        """Filtra los valores del listbox según lo que el usuario escribe."""
        val = entry.get().lower()
        listbox.delete(0, tk.END)
        for item in lista_completa:
            if val in item.lower():
                listbox.insert(tk.END, item)
        
        # Seleccionar automáticamente el primero si hay coincidencias y se presiona Enter
        if event.keysym == "Return" and listbox.size() > 0:
            listbox.selection_set(0)
            listbox.activate(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = HeladeriaApp(root)
    root.mainloop()