import sys
import requests

API_URL = "http://127.0.0.1:5000"

def mostrar_menu():
    print("\n" + "="*50)
    print("    SISTEMA DE GESTIÓN DE TAREAS - CLIENTE CONSOLA")
    print("="*50)
    print("1. Registrar nuevo usuario (POST /registro)")
    print("2. Iniciar sesión (POST /login)")
    print("3. Salir")
    print("="*50)

def registrar_usuario():
    print("\n--- REGISTRO DE USUARIO ---")
    usuario = input("Ingrese nombre de usuario: ").strip()
    password = input("Ingrese contraseña: ").strip()

    if not usuario or not password:
        print("[!] Error: El usuario y la contraseña no pueden estar vacíos.")
        return

    payload = {
        "usuario": usuario,
        "contraseña": password
    }

    try:
        respuesta = requests.post(f"{API_URL}/registro", json=payload, timeout=10)
        print(f"\n[Código HTTP: {respuesta.status_code}]")
        datos = respuesta.json()
        if respuesta.status_code == 201:
            print(f"[✓] {datos.get('mensaje')}")
            print(f"    ID de usuario asignado: {datos.get('id')}")
        else:
            print(f"[✗] Error: {datos.get('error')}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Error de conexión con el servidor: {e}")

def iniciar_sesion():
    print("\n--- INICIO DE SESIÓN ---")
    usuario = input("Ingrese nombre de usuario: ").strip()
    password = input("Ingrese contraseña: ").strip()

    if not usuario or not password:
        print("[!] Error: El usuario y la contraseña no pueden estar vacíos.")
        return None

    payload = {
        "usuario": usuario,
        "contraseña": password
    }

    try:
        respuesta = requests.post(f"{API_URL}/login", json=payload, timeout=10)
        print(f"\n[Código HTTP: {respuesta.status_code}]")
        datos = respuesta.json()
        if respuesta.status_code == 200:
            print(f"[✓] {datos.get('mensaje')}")
            print(f"    Usuario: {datos.get('usuario')} (ID: {datos.get('usuario_id')})")
            print("[✓] Autenticación verificada: Redirigiendo a la gestión de tareas...")
            # Redirección automática al HTML de bienvenida y tareas
            consultar_tareas()
            return datos
        else:
            print(f"[✗] Error: {datos.get('error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Error de conexión con el servidor: {e}")
        return None

def consultar_tareas():
    print("\n--- CONSULTANDO BIENVENIDA DE TAREAS (GET /tareas) ---")
    try:
        respuesta = requests.get(f"{API_URL}/tareas", timeout=10)
        print(f"[Código HTTP: {respuesta.status_code}]")
        if respuesta.status_code == 200:
            print("[✓] Respuesta HTML recibida con éxito:")
            print("-" * 40)
            # Mostramos un fragmento representativo del HTML en consola
            lineas = respuesta.text.strip().split("\n")
            preview = "\n".join(lineas[:15])
            print(preview)
            if len(lineas) > 15:
                print("... [HTML renderizado completo en el navegador] ...")
            print("-" * 40)
            print(f"[i] Puedes abrir http://127.0.0.1:5000/tareas en tu navegador para ver la interfaz gráfica.")
        else:
            print(f"[✗] Error al obtener tareas: {respuesta.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Error de conexión con el servidor: {e}")

def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-3): ").strip()
        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            iniciar_sesion()
        elif opcion == "3":
            print("\n¡Gracias por utilizar el cliente de consola! Saliendo...")
            sys.exit(0)
        else:
            print("[!] Opción inválida. Por favor seleccione del 1 al 3.")

if __name__ == "__main__":
    main()
