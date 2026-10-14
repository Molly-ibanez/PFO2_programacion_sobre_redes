import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB_NAME = "tareas.db"

# =====================================================================
# INICIALIZACIÓN DE LA BASE DE DATOS SQLITE
# =====================================================================
def inicializar_db():
    """Crea las tablas necesarias si no existen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabla de usuarios con contraseñas hasheadas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            creado_en TEXT NOT NULL
        )
    """)
    # Tabla de tareas para completar el sistema de gestión
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            completada INTEGER DEFAULT 0,
            creada_en TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)
    conn.commit()
    conn.close()

def obtener_conexion():
    """Retorna una conexión a SQLite con timeout de 15s y modo WAL anti-bloqueos."""
    conn = sqlite3.connect(DB_NAME, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn

# =====================================================================
# ENDPOINT 1: REGISTRO DE USUARIOS (POST /registro)
# =====================================================================
@app.route('/registro', methods=['POST'])
def registro():
    """
    Recibe {"usuario": "nombre", "contraseña": "1234"}.
    Hashea la contraseña y persiste en SQLite.
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Formato JSON inválido o ausente"}), 400

    usuario = datos.get('usuario')
    # Admite tanto 'contraseña' como 'password' por compatibilidad
    password = datos.get('contraseña') or datos.get('password')

    if not usuario or not password:
        return jsonify({"error": "Los campos 'usuario' y 'contraseña' son obligatorios"}), 400

    # Hasheo seguro usando werkzeug.security (PBKDF2/SHA-256 con salt)
    hash_seguro = generate_password_hash(password)
    fecha_creacion = datetime.now().isoformat()

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (usuario, password_hash, creado_en) VALUES (?, ?, ?)",
            (usuario.strip(), hash_seguro, fecha_creacion)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()
        print(f"[SERVIDOR] Usuario registrado con éxito: '{usuario}' (ID: {nuevo_id})")
        return jsonify({
            "mensaje": f"Usuario '{usuario}' registrado con éxito",
            "id": nuevo_id
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": f"El usuario '{usuario}' ya existe en el sistema"}), 409
    except sqlite3.Error as e:
        return jsonify({"error": f"Error en base de datos: {str(e)}"}), 500

# =====================================================================
# ENDPOINT 2: INICIO DE SESIÓN (POST /login)
# =====================================================================
@app.route('/login', methods=['POST'])
def login():
    """
    Verifica las credenciales comparando la contraseña en texto plano
    con el hash almacenado en SQLite.
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Formato JSON inválido o ausente"}), 400

    usuario = datos.get('usuario')
    password = datos.get('contraseña') or datos.get('password')

    if not usuario or not password:
        return jsonify({"error": "Los campos 'usuario' y 'contraseña' son obligatorios"}), 400

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, password_hash FROM usuarios WHERE usuario = ?", (usuario.strip(),))
        fila = cursor.fetchone()
        conn.close()

        # Seguridad: respuesta genérica 401 para evitar enumeración de usuarios
        if not fila or not check_password_hash(fila['password_hash'], password):
            print(f"[SERVIDOR] Login fallido para: '{usuario}'")
            return jsonify({"error": "Credenciales inválidas"}), 401

        print(f"[SERVIDOR] Login exitoso para: '{fila['usuario']}'")
        return jsonify({
            "mensaje": f"Bienvenido/a, {fila['usuario']}. Acceso concedido.",
            "usuario": fila['usuario'],
            "usuario_id": fila['id'],
            "acceso_tareas": True
        }), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Error en base de datos: {str(e)}"}), 500

# =====================================================================
# ENDPOINT 3: GESTIÓN DE TAREAS (GET /tareas)
# =====================================================================
HTML_BIENVENIDA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Gestión de Tareas - PFO 2</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1f2937, #111827);
            color: #f3f4f6;
            margin: 0;
            padding: 40px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
        }
        .card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 32px;
            max-width: 650px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            text-align: center;
        }
        h1 {
            color: #38bdf8;
            margin-bottom: 8px;
        }
        p.subtitle {
            color: #94a3b8;
            font-size: 1.1em;
            margin-bottom: 24px;
        }
        .features {
            text-align: left;
            background: #0f172a;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 24px;
            border-left: 4px solid #38bdf8;
        }
        .features li {
            margin: 8px 0;
            color: #cbd5e1;
        }
        .status-badge {
            display: inline-block;
            background-color: #10b981;
            color: #ffffff;
            font-size: 0.85em;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>¡Bienvenido al Sistema de Gestión de Tareas!</h1>
        <p class="subtitle">Práctica Formativa Obligatoria 2 (PFO 2) - Programación sobre Redes</p>
        <div class="features">
            <strong>Endpoints de la API REST activos:</strong>
            <ul>
                <li><code>POST /registro</code>: Alta segura con contraseña hasheada en SQLite.</li>
                <li><code>POST /login</code>: Autenticación verificando hashes criptográficos.</li>
                <li><code>GET /tareas</code>: Vista HTML de bienvenida y estado del servicio.</li>
            </ul>
        </div>
        <div class="status-badge">API REST Online & Conexión SQLite Activa</div>
    </div>
</body>
</html>
"""

@app.route('/tareas', methods=['GET'])
def tareas():
    """Devuelve un HTML de bienvenida según lo solicitado en la consigna."""
    return render_template_string(HTML_BIENVENIDA)

if __name__ == '__main__':
    inicializar_db()
    print("[*] Iniciando API Flask en http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
