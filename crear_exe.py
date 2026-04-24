#!/usr/bin/env python
"""
Script para generar el .exe de la aplicacion
Ejecuta este archivo con: python crear_exe.py
"""
import subprocess
import sys
import os

# Cambiar al directorio de la aplicacion
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("GENERADOR DE EJECUTABLE - Sistema POS Heladeria")
print("=" * 60)

# 1. Desinstalar pathlib (causa conflictos con PyInstaller)
print("\n[1] Desinstalando pathlib (incompatible con PyInstaller)...")
subprocess.run([sys.executable, "-m", "pip", "uninstall", "pathlib", "-y"], 
               capture_output=True)
print("[OK] Accion completada")

# 2. Ejecutar PyInstaller
print("\n[2] Compilando aplicacion a .exe...")
print("    Esto puede tardar 1-2 minutos...")

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", "SistemaPOS",
    "--add-data", "clientes.json;.",
    "--add-data", "facturas.json;.",
    "--add-data", "inventario_helados.json;.",
    "--add-data", "index.html;.",
    "--add-data", "style.css;.",
    "--add-data", "app.js;.",
    "main.py"
]

resultado = subprocess.run(cmd)

if resultado.returncode == 0:
    print("\n" + "=" * 60)
    print("[OK] EXITO! Archivo .exe creado correctamente")
    print("=" * 60)
    print(f"\nUbicacion: {os.path.abspath('dist/SistemaPOS.exe')}")
    print("\n[OK] Puedes ejecutar la aplicacion desde:")
    print("  - dist/SistemaPOS.exe")
    print("  - O copiar dist/SistemaPOS.exe a cualquier lugar")
    print("\nNota: Los archivos de datos (JSON, HTML, etc.) se incluyen")
    print("      automaticamente en el .exe")
else:
    print("\n[ERROR] Error al compilar. Revisa los mensajes arriba.")
    print("Posibles soluciones:")
    print("  1. Asegurate de tener PyInstaller instalado: pip install pyinstaller")
    print("  2. Verifica que todos los archivos existan en el directorio")

input("\nPresiona Enter para cerrar...")
