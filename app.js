let miGrafico = null; 
let facturasGlobales = []; // Guardamos todas las facturas aquí

async function inicializarDashboard() {
    try {
        const respuesta = await fetch('facturas.json?t=' + new Date().getTime());
        if (!respuesta.ok) throw new Error("No se pudo cargar facturas.json");
        
        facturasGlobales = await respuesta.json();
        
        llenarSelectorMeses();
        
        // Escuchamos cuando el usuario cambie el mes o el día
        document.getElementById('filtro-mes').addEventListener('change', () => {
            document.getElementById('filtro-dia').value = ""; // Limpiar día si cambia mes
            procesarDatos();
        });

        document.getElementById('filtro-dia').addEventListener('change', () => {
            document.getElementById('filtro-mes').value = "todos"; // Limpiar mes si cambia día
            procesarDatos();
        });

        procesarDatos();

    } catch (error) {
        console.error("Esperando datos...", error);
    }
}

function llenarSelectorMeses() {
    const selector = document.getElementById('filtro-mes');
    const mesesUnicos = new Set(); // Un Set evita que haya meses repetidos

    facturasGlobales.forEach(f => {
        if (f.fecha) {
            // Extraemos solo el Año y el Mes (Ej: "2026-03")
            const anioMes = f.fecha.substring(0, 7); 
            mesesUnicos.add(anioMes);
        }
    });

    // Convertimos el Set a Array, lo ordenamos de más nuevo a más viejo
    const mesesOrdenados = Array.from(mesesUnicos).sort().reverse();

    mesesOrdenados.forEach(mes => {
        const opcion = document.createElement('option');
        opcion.value = mes;
        opcion.textContent = mes;
        selector.appendChild(opcion);
    });
}

function procesarDatos() {
    const mesFiltro = document.getElementById('filtro-mes').value;
    const diaFiltro = document.getElementById('filtro-dia').value;

    let totalIngresos = 0;
    let totalCosto = 0;
    let totalUtilidad = 0;
    let totalFacturas = 0;
    
    const etiquetasGrafico = [];
    const datosGrafico = [];

    const ventasPorProducto = {};
    const ventasPorDia = {};
    const ventasPorMes = {};
    const ventasPorMetodo = {}; // <-- Nuevo

    facturasGlobales.forEach((factura, index) => {
        // Validamos si la factura tiene fecha
        if (!factura.fecha) return;

        const fechaCompleta = factura.fecha;
        const diaCorta = fechaCompleta.split(" ")[0]; // YYYY-MM-DD
        const mesCorta = fechaCompleta.substring(0, 7); // YYYY-MM

        // Llenamos el diccionario de Meses (Este no se filtra, siempre muestra todos los meses)
        if (!ventasPorMes[mesCorta]) {
            ventasPorMes[mesCorta] = { ingresos: 0, utilidad: 0, pagos: {} };
        }
        ventasPorMes[mesCorta].ingresos += factura.total_venta;
        ventasPorMes[mesCorta].utilidad += factura.utilidad;
        
        const m_mes = factura.metodo_pago || "Efectivo";
        if (!ventasPorMes[mesCorta].pagos[m_mes]) ventasPorMes[mesCorta].pagos[m_mes] = 0;
        ventasPorMes[mesCorta].pagos[m_mes] += factura.total_venta;

        // FILTROS
        if (mesFiltro !== 'todos' && mesCorta !== mesFiltro) return;
        if (diaFiltro !== '' && diaCorta !== diaFiltro) return;

        // --- A PARTIR DE AQUÍ, SOLO SE PROCESA LO QUE PASÓ EL FILTRO ---
        totalIngresos += factura.total_venta;
        totalCosto += factura.total_costo || 0;
        totalUtilidad += factura.utilidad;
        totalFacturas++;
        
        etiquetasGrafico.push(`Venta #${index + 1}`);
        datosGrafico.push(factura.total_venta);

        // Agrupar por Día (Ahora guarda ingresos, costo Y utilidad)
        if (!ventasPorDia[diaCorta]) {
            ventasPorDia[diaCorta] = { ingresos: 0, costo: 0, utilidad: 0, pagos: {} };
        }
        ventasPorDia[diaCorta].ingresos += factura.total_venta;
        ventasPorDia[diaCorta].costo += factura.total_costo || 0;
        ventasPorDia[diaCorta].utilidad += factura.utilidad;

        // Agrupar pagos por día
        const m = factura.metodo_pago || "Efectivo";
        if (!ventasPorDia[diaCorta].pagos[m]) {
            ventasPorDia[diaCorta].pagos[m] = 0;
        }
        ventasPorDia[diaCorta].pagos[m] += factura.total_venta;

        // Agrupar por Método de Pago (Nuevo)
        const metodo = factura.metodo_pago || "Efectivo";
        if (!ventasPorMetodo[metodo]) {
            ventasPorMetodo[metodo] = 0;
        }
        ventasPorMetodo[metodo] += factura.total_venta;

        // Agrupar por Producto
        if (factura.detalle_productos) {
            factura.detalle_productos.forEach(item => {
                if (!ventasPorProducto[item.sabor]) {
                    ventasPorProducto[item.sabor] = { cantidad: 0, ingresos: 0 };
                }
                ventasPorProducto[item.sabor].cantidad += item.cantidad;
                ventasPorProducto[item.sabor].ingresos += item.venta_total;
            });
        }
    });

    // Actualizamos KPIs
    document.getElementById('kpi-ingresos').innerText = "$" + totalIngresos.toLocaleString();
    document.getElementById('kpi-costo').innerText = "$" + totalCosto.toLocaleString();
    document.getElementById('kpi-utilidad').innerText = "$" + totalUtilidad.toLocaleString();
    document.getElementById('kpi-facturas').innerText = totalFacturas;

    // Cálculo 70/30
    const p70 = Math.floor(totalUtilidad * 0.7);
    const p30 = Math.floor(totalUtilidad * 0.3);
    document.getElementById('kpi-70').innerText = "$" + p70.toLocaleString();
    document.getElementById('kpi-30').innerText = "$" + p30.toLocaleString();

    // Actualizamos KPIs de Pago
    if (document.getElementById('kpi-pagos')) {
        actualizarKPIPagos(ventasPorMetodo);
    }
    
    // Dibujamos
    dibujarGrafico(etiquetasGrafico, datosGrafico);
    renderizarTablaCompleja('tabla-dias', ventasPorDia);
    renderizarTablaCompleja('tabla-meses', ventasPorMes);
    
    // La tabla de productos completa
    renderizarTablaProductos(ventasPorProducto, totalIngresos);
    
    // Generar análisis
    generarAnalisisVentas(ventasPorProducto, totalIngresos, ventasPorDia, totalUtilidad);
}

function dibujarGrafico(etiquetas, datos) {
    const contexto = document.getElementById('graficoVentas').getContext('2d');
    if (miGrafico) miGrafico.destroy();

    miGrafico = new Chart(contexto, {
        type: 'line', 
        data: {
            labels: etiquetas,
            datasets: [{
                label: 'Ingresos por Venta ($)',
                data: datos,
                backgroundColor: 'rgba(76, 175, 80, 0.2)', // Cambiado a verdecito financiero
                borderColor: 'rgba(76, 175, 80, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// Nueva función para tablas que muestran 3 columnas (Llave, Ingresos, Utilidad)
function renderizarTablaCompleja(idTabla, datosAgrupados) {
    const tbody = document.querySelector(`#${idTabla} tbody`);
    tbody.innerHTML = ""; 
    
    // Ordenar de más reciente a más antiguo (alfabéticamente por la llave de fecha)
    const arrayDatos = Object.entries(datosAgrupados).sort((a, b) => b[0].localeCompare(a[0]));
    
    arrayDatos.forEach(([llave, datos]) => {
        // Generar resumen de pagos si existe
        let resumenPagos = "";
        if (datos.pagos) {
            resumenPagos = Object.entries(datos.pagos)
                .map(([metodo, total]) => `<span title="${metodo}" style="font-size: 0.8rem; background: #eee; padding: 2px 5px; border-radius: 3px; margin-right: 3px;">${metodo[0]}: $${total.toLocaleString()}</span>`)
                .join(" ");
        }

        if (idTabla === 'tabla-dias') {
            // Cálculos específicos para la tabla diaria
            const p70 = Math.floor(datos.utilidad * 0.7);
            const p30 = Math.floor(datos.utilidad * 0.3);
            
            tbody.innerHTML += `<tr>
                <td><strong>${llave}</strong></td>
                <td>$${datos.ingresos.toLocaleString()}</td>
                <td>$${(datos.costo || 0).toLocaleString()}</td>
                <td style="color: #2E7D32; font-weight: bold;">$${datos.utilidad.toLocaleString()}</td>
                <td style="color: #673AB7;">$${p70.toLocaleString()}</td>
                <td style="color: #9575CD;">$${p30.toLocaleString()}</td>
                <td>${resumenPagos || "-"}</td>
            </tr>`;
        } else {
            // Formato estándar para la tabla mensual
            tbody.innerHTML += `<tr>
                <td><strong>${llave}</strong></td>
                <td>$${datos.ingresos.toLocaleString()}</td>
                <td style="color: #2E7D32; font-weight: bold;">$${datos.utilidad.toLocaleString()}</td>
                <td>${resumenPagos || "-"}</td>
            </tr>`;
        }
    });
}

function renderizarTablaProductos(datosAgrupados, totalIngresos) {
    const tbody = document.querySelector('#tabla-productos-completa tbody');
    tbody.innerHTML = ""; 
    
    // Ordenar de mayor a menor ingreso
    const arrayDatos = Object.entries(datosAgrupados).sort((a, b) => b[1].ingresos - a[1].ingresos);
    
    arrayDatos.forEach(([sabor, datos]) => {
        const porcentaje = totalIngresos > 0 ? ((datos.ingresos / totalIngresos) * 100).toFixed(2) : 0;
        const barraProgreso = '<div style="background: linear-gradient(to right, #4CAF50, #81C784); width: ' + porcentaje + '%; height: 20px; border-radius: 3px; display: inline-block; min-width: 50px; color: white; font-size: 0.8rem; text-align: center; line-height: 20px;">' + porcentaje + '%</div>';
        
        tbody.innerHTML += `<tr>
            <td><strong>${sabor}</strong></td>
            <td style="text-align: center; font-weight: bold;">${datos.cantidad}</td>
            <td style="text-align: right;">$${datos.ingresos.toLocaleString()}</td>
            <td>${barraProgreso}</td>
        </tr>`;
    });
}

function generarAnalisisVentas(ventasPorProducto, totalIngresos, ventasPorDia, totalUtilidad) {
    const contenedor = document.getElementById('analisis-contenedor');
    let html = '';
    
    // Convertir a array y ordenar
    const productos = Object.entries(ventasPorProducto)
        .sort((a, b) => b[1].ingresos - a[1].ingresos)
        .map(([nombre, datos]) => ({
            nombre,
            cantidad: datos.cantidad,
            ingresos: datos.ingresos,
            porcentaje: (datos.ingresos / totalIngresos * 100).toFixed(2)
        }));
    
    // Calcular promedios
    const promedioVentasPorProducto = productos.length > 0 
        ? (totalIngresos / Object.keys(ventasPorProducto).length).toFixed(0)
        : 0;
    
    const productoEstrella = productos.length > 0 ? productos[0] : null;
    const productoDebil = productos.length > 0 ? productos[productos.length - 1] : null;
    
    // Análisis por día
    const diasConVentas = Object.keys(ventasPorDia).length;
    const promedioVentasDia = diasConVentas > 0 
        ? (totalIngresos / diasConVentas).toFixed(0)
        : 0;
    
    // Rentabilidad
    const margenUtilidad = totalIngresos > 0 
        ? ((totalUtilidad / totalIngresos) * 100).toFixed(1)
        : 0;
    
    html += '<ul style="list-style: none; padding: 0;">';
    
    // 1. Producto Estrella
    if (productoEstrella) {
        html += `<li style="margin: 15px 0; padding: 10px; background: #E8F5E9; border-radius: 5px; border-left: 4px solid #4CAF50;">
            <strong>⭐ Producto Estrella:</strong> ${productoEstrella.nombre} representa el <strong>${productoEstrella.porcentaje}%</strong> de los ingresos (${productoEstrella.cantidad} unidades vendidas). Este es tu producto más rentable, considera mantener su stock disponible.
        </li>`;
    }
    
    // 2. Producto Débil
    if (productoDebil && productoDebil.ingresos < (totalIngresos * 0.05)) {
        html += `<li style="margin: 15px 0; padding: 10px; background: #FFF3E0; border-radius: 5px; border-left: 4px solid #FF9800;">
            <strong>⚠️ Producto con Bajo Rendimiento:</strong> ${productoDebil.nombre} solo representa el <strong>${productoDebil.porcentaje}%</strong> de los ingresos. Considera revisar su popularidad o hacer promociones.
        </li>`;
    }
    
    // 3. Diversificación de Productos
    const productosVendidos = Object.keys(ventasPorProducto).length;
    if (productosVendidos >= 10) {
        html += `<li style="margin: 15px 0; padding: 10px; background: #E3F2FD; border-radius: 5px; border-left: 4px solid #1976D2;">
            <strong>✅ Buen Surtido:</strong> Estás vendiendo <strong>${productosVendidos} productos diferentes</strong>. Esto muestra una buena diversificación de ventas.
        </li>`;
    } else if (productosVendidos < 5) {
        html += `<li style="margin: 15px 0; padding: 10px; background: #FFF3E0; border-radius: 5px; border-left: 4px solid #FF9800;">
            <strong>💭 Concentración de Ventas:</strong> Solo estás vendiendo <strong>${productosVendidos} productos</strong>. Intenta impulsar otros sabores para diversificar.
        </li>`;
    }
    
    // 4. Desempeño Global
    html += `<li style="margin: 15px 0; padding: 10px; background: #F3E5F5; border-radius: 5px; border-left: 4px solid #9C27B0;">
        <strong>📈 Resumen del Desempeño:</strong> 
        <ul style="margin: 10px 0; padding-left: 20px;">
            <li>Días con ventas: <strong>${diasConVentas}</strong></li>
            <li>Promedio de ingresos por día: <strong>$${promedioVentasDia}</strong></li>
            <li>Margen de utilidad: <strong>${margenUtilidad}%</strong></li>
            <li>Promedio por producto: <strong>$${promedioVentasPorProducto}</strong></li>
        </ul>
    </li>`;
    
    // 5. Recomendaciones
    let recomendaciones = [];
    
    if (margenUtilidad < 30) {
        recomendaciones.push('Revisa tus costos de producción. El margen de utilidad está bajo.');
    }
    if (productosVendidos < 5) {
        recomendaciones.push('Expande tu catálogo y promociona nuevos sabores.');
    }
    if (productoEstrella && parseFloat(productoEstrella.porcentaje) > 40) {
        recomendaciones.push('Tu negocio depende mucho de un solo producto. Diversifica para reducir riesgos.');
    }
    
    if (recomendaciones.length > 0) {
        html += `<li style="margin: 15px 0; padding: 10px; background: #FCE4EC; border-radius: 5px; border-left: 4px solid #E91E63;">
            <strong>💡 Recomendaciones:</strong>
            <ul style="margin: 10px 0; padding-left: 20px;">
                ${recomendaciones.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        </li>`;
    }
    
    html += '</ul>';
    
    contenedor.innerHTML = html;
}

function actualizarKPIPagos(datos) {
    const contenedor = document.getElementById('kpi-pagos');
    let html = '<ul style="list-style: none; padding: 0; margin: 0;">';
    
    // Iteramos por los métodos encontrados
    Object.entries(datos).forEach(([metodo, total]) => {
        html += `<li style="margin-bottom: 5px;"><strong>${metodo}:</strong> $${total.toLocaleString()}</li>`;
    });
    
    html += '</ul>';
    contenedor.innerHTML = html;
}

function limpiarFiltros() {
    document.getElementById('filtro-mes').value = "todos";
    document.getElementById('filtro-dia').value = "";
    procesarDatos();
}

// Arrancamos todo
inicializarDashboard();
setInterval(() => {
    // Cuando el temporizador se dispara, leemos qué mes está seleccionado actualmente
    const mesActualSeleccionado = document.getElementById('filtro-mes').value;
    
    // Volvemos a descargar el JSON por si hubo ventas nuevas
    fetch('facturas.json?t=' + new Date().getTime())
        .then(res => res.json())
        .then(datos => {
            facturasGlobales = datos;
            procesarDatos(mesActualSeleccionado); // Reprocesamos respetando el filtro
        })
        .catch(e => console.log(e));
}, 5000);