# Tech y Print Solutions

Tech y Print Solutions es una aplicación web desarrollada con Flask que centraliza la gestión de solicitudes de impresión y soporte técnico para empresas o centros de impresión. El proyecto combina una experiencia de usuario moderna con un flujo de trabajo seguro, permitiendo que clientes y administradores interactúen sobre una misma plataforma.

## Características principales
- **Autenticación con roles**: Los usuarios pueden registrarse, iniciar sesión y acceder a un panel personalizado. Los administradores cuentan con vistas adicionales para gestionar solicitudes.
- **Solicitudes de impresión**: Permite subir archivos PDF, definir preferencias (color y tipo de faz) y almacenar el historial en la base de datos.
- **Servicio técnico**: Recoge incidencias de hardware o software, asociando cada petición al usuario que la reporta.
- **Panel administrativo**: Consolida todas las solicitudes de impresión y servicio para su revisión y seguimiento, con opción de eliminación.
- **Experiencia de interfaz**: Plantillas HTML con estilo responsivo y elementos animados que refuerzan la identidad visual de la marca.

## Arquitectura y componentes
- **`app.py`**: Punto de entrada de la aplicación. Configura Flask, la base de datos SQLite, Flask-Login y define las rutas principales (`/impresion`, `/servicio`, `/admin`, etc.). Gestiona la lógica de subida de archivos y el uso de sesiones.
- **`models.py`**: Contiene las clases `User`, `PrintRequest` y `ServiceRequest`, definidas con SQLAlchemy y extendiendo `UserMixin` para integrarse con Flask-Login.
- **`templates/`**: Plantillas Jinja2 que estructuran la interfaz (por ejemplo, `index.html`, `login.html`, `admin.html`). Heredan de `base.html`, que define la navegación y el pie de página.
- **`static/`**: Archivos estáticos como `styles.css` y recursos gráficos. El estilo se basa en un diseño oscuro con gradientes y microinteracciones.
- **`instance/techprint.db`**: Base de datos SQLite generada automáticamente al iniciar la aplicación. Se guarda en la carpeta `instance` para evitar su versionado accidental.
- **Carpeta `uploads/`** (generada en runtime): Almacena los archivos PDF cargados por los usuarios para luego poder ser descargados desde el panel.

## Flujo de usuario
1. **Registro**: Se valida la unicidad de nombre de usuario, correo y teléfono. Las contraseñas se almacenan con `generate_password_hash` (PBKDF2).
2. **Inicio de sesión**: Se autentica al usuario y se inicia sesión con Flask-Login. Las rutas críticas usan `@login_required`.
3. **Operaciones para clientes**:
   - Formulario de impresión (`/impresion`) con subida de PDF y preferencias.
   - Formulario de soporte (`/servicio`) para describir fallas en equipos.
4. **Operaciones para administradores**:
   - Vista `/admin` con el listado de todas las solicitudes.
   - Acceso a perfiles de usuario (`/profileADM/<id>`).
   - Acciones de mantenimiento como eliminar solicitudes.

## Modelo de datos
| Tabla | Campos relevantes | Descripción |
|-------|-------------------|-------------|
| `User` | `username`, `email`, `phone`, `password`, `type` | Representa a los usuarios autenticados. El campo `type` define si el rol es `admin` o `client`.
| `PrintRequest` | `filename`, `color`, `faz`, `user_id` | Guarda metadatos sobre cada archivo enviado para impresión.
| `ServiceRequest` | `device_name`, `description`, `user_id` | Registra incidentes técnicos reportados por los clientes.

## Requisitos previos
- Python 3.10 o superior.
- Dependencias listadas en `requirements.txt` (Flask, Flask-Login, Flask-SQLAlchemy, SQLAlchemy, Gunicorn, etc.).

> **Nota:** El archivo `requirements.txt` incluye Gunicorn dos veces; puedes limpiar la línea duplicada antes de instalar si lo deseas.

## Ejecución local
1. Crear y activar un entorno virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Definir variables opcionales (por ejemplo `FLASK_ENV=development`). Considera cambiar `app.secret_key` en `app.py` por una clave segura tomada de la variable de entorno `SECRET_KEY`.
4. Ejecutar la aplicación:
   ```bash
   python app.py
   ```
5. Accede a `http://localhost:5000`. El servidor crea la base de datos y la carpeta `uploads/` en el primer arranque.

## Despliegue
- El proyecto puede ejecutarse con Gunicorn para entornos productivos:
  ```bash
  gunicorn --bind 0.0.0.0:8000 app:app
  ```
- Configura variables de entorno como `SECRET_KEY` y `SQLALCHEMY_DATABASE_URI` para separar credenciales de la configuración por defecto.
- Al usar almacenamiento persistente (S3, Azure Blob, etc.) para archivos, actualiza `UPLOAD_FOLDER` en `app.config` y el mecanismo de descargas (`send_from_directory`).

## Consideraciones de seguridad y mantenimiento
- Implementa HTTPS y políticas de tamaño máximo de archivo si la aplicación se expone públicamente.
- Añade migraciones con Flask-Migrate para cambios de esquema futuros.
- Integra un sistema de notificaciones o correo (por ejemplo, Flask-Mail) para avisar al usuario sobre el estado de sus solicitudes.
- Reemplaza la clave secreta hardcodeada y utiliza sesiones seguras en producción.

## Estructura del repositorio
```
TechYPrintSolutions/
├── app.py
├── models.py
├── requirements.txt
├── static/
│   └── styles.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── impresion.html
│   ├── login.html
│   ├── profile.html
│   ├── register.html
│   └── servicio.html
├── instance/
│   └── techprint.db
└── README.md
```

Este README sirve como punto de partida para entender la arquitectura y facilitar el despliegue o extensión del sistema.
