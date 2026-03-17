let miGrafico = null; 
let facturasGlobales = []; // Guardamos todas las facturas aquí

async function inicializarDashboard() {
    try {
        const respuesta = await fetch('facturas.json?t=' + new Date().getTime());
        if (!respuesta.ok) throw new Error("No se pudo cargar facturas.json");
        
        facturasGlobales = await respuesta.json();
        
        llenarSelectorMeses();
        
        // Escuchamos cuando el usuario cambie el mes en el selector
        document.getElementById('filtro-mes').addEventListener('change', (evento) => {
            procesarDatos(evento.target.value);
        });

        // Procesamos los datos por primera vez (mostrando todo)
        procesarDatos('todos');

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

function procesarDatos(mesFiltro) {
    let totalIngresos = 0;
    let totalUtilidad = 0;
    let totalFacturas = 0;
    
    const etiquetasGrafico = [];
    const datosGrafico = [];

    const ventasPorProducto = {};
    const ventasPorDia = {};
    const ventasPorMes = {}; // ¡NUEVO!

    facturasGlobales.forEach((factura, index) => {
        // Validamos si la factura tiene fecha
        if (!factura.fecha) return;

        const fechaCompleta = factura.fecha;
        const diaCorta = fechaCompleta.split(" ")[0]; // YYYY-MM-DD
        const mesCorta = fechaCompleta.substring(0, 7); // YYYY-MM

        // Llenamos el diccionario de Meses (Este no se filtra, siempre muestra todos los meses)
        if (!ventasPorMes[mesCorta]) {
            ventasPorMes[mesCorta] = { ingresos: 0, utilidad: 0 };
        }
        ventasPorMes[mesCorta].ingresos += factura.total_venta;
        ventasPorMes[mesCorta].utilidad += factura.utilidad;

        // EL FILTRO MÁGICO: Si seleccionamos un mes y la factura no es de ese mes, la ignoramos para el resto
        if (mesFiltro !== 'todos' && mesCorta !== mesFiltro) {
            return; 
        }

        // --- A PARTIR DE AQUÍ, SOLO SE PROCESA LO QUE PASÓ EL FILTRO ---
        totalIngresos += factura.total_venta;
        totalUtilidad += factura.utilidad;
        totalFacturas++;
        
        etiquetasGrafico.push(`Venta #${index + 1}`);
        datosGrafico.push(factura.total_venta);

        // Agrupar por Día (Ahora guarda ingresos Y ganancia)
        if (!ventasPorDia[diaCorta]) {
            ventasPorDia[diaCorta] = { ingresos: 0, utilidad: 0 };
        }
        ventasPorDia[diaCorta].ingresos += factura.total_venta;
        ventasPorDia[diaCorta].utilidad += factura.utilidad;

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
    document.getElementById('kpi-utilidad').innerText = "$" + totalUtilidad.toLocaleString();
    document.getElementById('kpi-facturas').innerText = totalFacturas;

    // Dibujamos
    dibujarGrafico(etiquetasGrafico, datosGrafico);
    renderizarTablaCompleja('tabla-dias', ventasPorDia);
    renderizarTablaCompleja('tabla-meses', ventasPorMes);
    
    // La tabla de productos sigue usando una función ligeramente diferente porque tiene "cantidad" en vez de "utilidad"
    renderizarTablaProductos(ventasPorProducto);
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
        // Le ponemos un color verde a la utilidad para que resalte
        tbody.innerHTML += `<tr>
            <td><strong>${llave}</strong></td>
            <td>$${datos.ingresos.toLocaleString()}</td>
            <td style="color: #2E7D32; font-weight: bold;">$${datos.utilidad.toLocaleString()}</td>
        </tr>`;
    });
}

function renderizarTablaProductos(datosAgrupados) {
    const tbody = document.querySelector('#tabla-productos tbody');
    tbody.innerHTML = ""; 
    const arrayDatos = Object.entries(datosAgrupados).sort((a, b) => b[1].ingresos - a[1].ingresos);
    arrayDatos.forEach(([sabor, datos]) => {
        tbody.innerHTML += `<tr>
            <td>${sabor}</td>
            <td>${datos.cantidad}</td>
            <td>$${datos.ingresos.toLocaleString()}</td>
        </tr>`;
    });
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