# PFO 2: Sistema de Gestión de Tareas con API y Base de Datos

Este repositorio contiene la solución completa a la **Práctica Formativa Obligatoria 2 (PFO 2)** de la materia **Programación sobre Redes** (Tecnicatura Superior en Desarrollo de Software a Distancia - IFTS Nº 29).

El proyecto implementa una **API REST** desarrollada con **Flask** y persistencia en **SQLite**, integrando autenticación de usuarios con contraseñas protegidas mediante algoritmos de hash criptográfico unidireccional y un cliente en consola interactivo.

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.12
* **Framework Web / API REST:** Flask
* **Seguridad y Criptografía:** `werkzeug.security` (`generate_password_hash`, `check_password_hash`)
* **Base de Datos:** SQLite3 (módulo nativo `sqlite3` de Python) optimizado con **Write-Ahead Logging (WAL)**
* **Cliente HTTP:** Módulo `requests`

---

## 📁 Estructura del Proyecto

```text
pfo2_gestion_tareas/
├── servidor.py          # API REST en Flask con persistencia en SQLite
├── cliente.py           # Cliente en consola interactivo (menú con redirección automática)
├── tareas.db            # Base de datos SQLite (generada automáticamente)
├── index.html           # Documentación web para publicar en GitHub Pages
├── .gitignore           # Exclusión de archivos binarios y base de datos
└── README.md            # Documentación completa y respuestas conceptuales
```

---


---

## 🔄 Flujo de la Aplicación y Arquitectura del Cliente

A diferencia de un esquema abierto, el cliente de consola implementa un flujo de acceso seguro y desacoplado:

1. **Menú Inicial:** Ofrece exclusivamente las opciones de registro, inicio de sesión y salida:
   * `1. Registrar nuevo usuario (POST /registro)`
   * `2. Iniciar sesión (POST /login)`
   * `3. Salir`
2. **Acceso Seguro a Tareas por Redirección:** La gestión/bienvenida de tareas (`GET /tareas`) no se expone a usuarios anónimos en el menú. Al iniciar sesión con éxito (`200 OK`), el cliente **redirige automáticamente** consumiendo el endpoint `GET /tareas`, mostrando la confirmación en consola e indicando el acceso web en el navegador.

---
## 🚀 Endpoints de la API REST

### 1. Registro de Usuarios (`POST /registro`)
* **Descripción:** Da de alta un nuevo usuario en la base de datos SQLite. La contraseña se hashea antes de almacenarse; nunca se guarda en texto plano.
* **Content-Type:** `application/json`
* **Cuerpo de la petición:**
  ```json
  {
    "usuario": "alan_redes",
    "contraseña": "MiPasswordSeguro2026!"
  }
  ```
* **Respuestas:**
  * `201 Created`: Usuario registrado con éxito (`{"mensaje": "...", "id": 1}`).
  * `400 Bad Request`: Formato inválido o campos faltantes.
  * `409 Conflict`: El nombre de usuario ya existe en el sistema.

### 2. Inicio de Sesión (`POST /login`)
* **Descripción:** Valida las credenciales comparando la contraseña enviada contra el hash criptográfico almacenado en SQLite.
* **Content-Type:** `application/json`
* **Cuerpo de la petición:**
  ```json
  {
    "usuario": "alan_redes",
    "contraseña": "MiPasswordSeguro2026!"
  }
  ```
* **Respuestas:**
  * `200 OK`: Credenciales válidas y acceso a las tareas concedido (`{"acceso_tareas": true, ...}`).
  * `401 Unauthorized`: `Credenciales inválidas` (mensaje unificado de seguridad para mitigar la enumeración de usuarios).

### 3. Vista de Bienvenida a Tareas (`GET /tareas`)
* **Descripción:** Retorna una interfaz HTML con el mensaje de bienvenida y estado del servicio.
* **Respuesta:**
  * `200 OK`: Documento `text/html` renderizado.

---


---

## ⚙️ Concurrencia y Resiliencia en la Base de Datos

Para evitar bloqueos y problemas de tiempo de espera (`Read timed out` o `database is locked`) entre transacciones concurrentes de lectura y escritura:
* **Modo WAL (`PRAGMA journal_mode=WAL;`):** Habilita el *Write-Ahead Logging*, permitiendo que las consultas de lectura (`SELECT`) y las operaciones de inserción (`INSERT`) se ejecuten concurrentemente sin interferencias.
* **Busy Timeout (`PRAGMA busy_timeout=5000;`):** Define un tiempo de tolerancia de hasta 5 segundos para que SQLite resuelva transacciones concurrentes antes de rechazar una operación.
* **Gestores de Contexto (`with`):** Aseguran la confirmación (*commit*) y el cierre oportuno de cada conexión liberando los recursos de inmediato.

---
## 💻 Instrucciones de Instalación y Ejecución

### 1. Clonar el Repositorio e Instalar Dependencias
```bash
git clone https://github.com/TU_USUARIO/pfo2-gestion-tareas.git
cd pfo2-gestion-tareas

# Crear entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate  # En Linux/macOS
# venv\Scripts\activate   # En Windows

# Instalar dependencias
pip install Flask requests
```

### 2. Iniciar el Servidor API
En una primera terminal, ejecutar:
```bash
python3 servidor.py
```
El servidor inicializará automáticamente el archivo `tareas.db` y quedará escuchando en `http://127.0.0.1:5000`.

### 3. Ejecutar el Cliente en Consola
En una segunda terminal, ejecutar:
```bash
python3 cliente.py
```
Aparecerá un menú interactivo con las siguientes opciones:
1. Registrar nuevo usuario (`POST /registro`).
2. Iniciar sesión (`POST /login` - valida credenciales y redirige automáticamente a tareas).
3. Salir.

##

---

## 🌐 Publicación en GitHub Pages

Para cumplir con el requerimiento de alojar el proyecto en GitHub Pages:
1. Subir el archivo `index.html` incluido en este repositorio a la raíz de tu proyecto en GitHub.
2. Ir a **Settings** (Configuración) de tu repositorio en GitHub.
3. En el menú lateral izquierdo, seleccionar **Pages**.
4. En **Build and deployment** -> **Branch**, seleccionar `main` (o `master`) y carpeta `/(root)`.
5. Hacer clic en **Save**. En un par de minutos tu sitio estará en vivo en `https://TU_USUARIO.github.io/TU_REPOSITORIO/`.

---

## 📚 Respuestas Conceptuales

### 1. ¿Por qué hashear contraseñas?
Almacenar contraseñas en texto plano es una de las vulnerabilidades más críticas en la arquitectura cliente-servidor:
1. **Irreversibilidad (Función Unidireccional):** Un algoritmo de hash criptográfico (como PBKDF2, bcrypt o scrypt) transforma una cadena de texto en un resumen alfanumérico fijo que no se puede revertir matemáticamente para obtener la contraseña original.
2. **Mitigación frente a Brechas de Seguridad:** Si un atacante logra acceder a la base de datos SQLite mediante una inyección SQL o una copia no autorizada del archivo `.db`, solo obtendrá los hashes y no las contraseñas reales de los usuarios.
3. **Uso de Salting (Sal Criptográfica):** Las librerías modernas como `werkzeug.security` agregan una sal aleatoria antes de generar el hash, lo que impide ataques mediante **Tablas Arcoíris (*Rainbow Tables*)** y ataques de diccionario precalculados, garantizando que dos usuarios con la misma contraseña tengan hashes completamente diferentes.
4. **Prevención de Enumeración de Usuarios:** Complementando el hasheo de contraseñas, el servidor emite respuestas de autenticación homogéneas (`Credenciales inválidas`) tanto si el usuario no existe como si la clave es incorrecta, evitando que atacantes descubran qué identidades están registradas en el sistema.

### 2. Ventajas de usar SQLite en este proyecto
1. **Serverless (Sin Servidor Autónomo):** A diferencia de bases de datos tradicionales como MySQL o PostgreSQL, SQLite no requiere un proceso demonio o servicio de base de datos ejecutándose en segundo plano; se embebe directamente en el proceso de Python.
2. **Almacenamiento Autocontenido en un Solo Archivo:** Toda la base de datos (tablas, índices, datos) se almacena en un único archivo en disco (`tareas.db`), lo que facilita la portabilidad, el empaquetado y las copias de seguridad.
3. **Cero Configuración (*Zero-Configuration*):** No requiere configuración de usuarios de base de datos, contraseñas de red ni puertos de conexión adicionales, agilizando el desarrollo y las pruebas locales.
4. **Confiabilidad y Transaccionalidad ACID:** Cumple con las propiedades de Atomicidad, Consistencia, Aislamiento y Durabilidad, asegurando que ante una desconexión o fallo, la base de datos conserve su integridad sin corromperse.
