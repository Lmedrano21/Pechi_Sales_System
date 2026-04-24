#!/usr/bin/env python
"""
Script para empaquetar la aplicación para distribución
Crea una carpeta lista para enviar a otros PCs
"""
import shutil
import os

# Archivos necesarios
CARPETA_ORIGEN = r"c:\Users\Sharith Pk\Desktop\Nueva carpeta\dist"
CARPETA_DESTINO = r"c:\Users\Sharith Pk\Desktop\SistemaPOS_v1"

# Crear carpeta de distribución
if os.path.exists(CARPETA_DESTINO):
    shutil.rmtree(CARPETA_DESTINO)
    
os.makedirs(CARPETA_DESTINO, exist_ok=True)

# Copiar los archivos necesarios
archivos = [
    "frontend.exe",
    "clientes.json",
    "facturas.json",
    "inventario_helados.json",
    "index.html",
    "style.css",
    "app.js"
]

print("=" * 60)
print("EMPAQUETANDO APLICACIÓN PARA DISTRIBUCIÓN")
print("=" * 60)

for archivo in archivos:
    ruta_origen = os.path.join(CARPETA_ORIGEN, archivo)
    ruta_destino = os.path.join(CARPETA_DESTINO, archivo)
    
    if os.path.exists(ruta_origen):
        shutil.copy2(ruta_origen, ruta_destino)
        tamaño = os.path.getsize(ruta_destino) / (1024 * 1024)  # MB
        print(f"✓ {archivo:<30} ({tamaño:.1f} MB)")
    else:
        print(f"✗ {archivo:<30} (NO ENCONTRADO)")

# Crear archivo README
readme = """# Sistema POS Integral Heladería

## Instalación

1. Descarga todos los archivos en la carpeta
2. Haz doble clic en **frontend.exe**
3. ¡Listo! La aplicación se abrirá automáticamente

## Requisitos del Sistema

- Windows 10 o superior
- No necesita Python instalado
- Conexión a internet (opcional, solo para WhatsApp)

## Archivos Incluidos

- **frontend.exe** - Aplicación principal
- **clientes.json** - Base de datos de clientes
- **facturas.json** - Historial de facturas
- **inventario_helados.json** - Inventario de productos
- **index.html, style.css, app.js** - Dashboard web

## Características

✓ Venta Rápida
✓ Facturación Detallada
✓ Gestión de Clientes (Crear, Editar, Eliminar)
✓ Inventario
✓ Dashboard Analítico
✓ Historial de Facturas

## Notas

- All archivos JSON deben estar en la misma carpeta que el .exe
- El dashboard se abre en http://localhost:8000
- Los datos se guardan automáticamente

¡Cualquier duda, contacta al equipo de soporte!
"""

with open(os.path.join(CARPETA_DESTINO, "README.txt"), "w", encoding="utf-8") as f:
    f.write(readme)

print("\n" + "=" * 60)
print(f"✓ Empaquetado completado!")
print(f"✓ Carpeta: {CARPETA_DESTINO}")
print("=" * 60)
print("\nAhora puedes:")
print(f"1. Copiar la carpeta '{os.path.basename(CARPETA_DESTINO)}' a otros PCs")
print("2. Compartirla por correo, USB, Dropbox, etc.")
print("3. Ejecutar frontend.exe en cualquier Windows")
print("\n¡importante: Mantén todos los archivos en la misma carpeta!")

input("\nPresiona Enter para cerrar...")
