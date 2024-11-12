from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from models import db, User, PrintRequest, ServiceRequest
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///techprint.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'

db.init_app(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Asegúrate de que la carpeta de subida exista
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.')
    
    return render_template('login.html')

# Ruta para descargar el archivo PDF
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Ruta de perfil de usuario (requiere inicio de sesión)
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# Ruta de perfil para administración
@app.route('/profileADM/<int:user_id>')
@login_required
def profileADM(user_id):
    user = User.query.get(user_id)
    if not user:
        return "Usuario no encontrado", 404
    return render_template('profile.html', user=user)

# Ruta para eliminar una solicitud de impresión
@app.route('/delete_print_request/<int:request_id>', methods=['POST'])
@login_required
def delete_print_request(request_id):
    print_request = PrintRequest.query.get(request_id)
    if print_request:
        db.session.delete(print_request)
        db.session.commit()
    return redirect(url_for('admin'))

# Ruta para eliminar una solicitud de servicio técnico
@app.route('/delete_service_request/<int:request_id>', methods=['POST'])
@login_required
def delete_service_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if service_request:
        db.session.delete(service_request)
        db.session.commit()
    return redirect(url_for('admin'))

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        
        # Comprobación de usuario existente
        existing_user = User.query.filter((User.username == username) | 
                                          (User.email == email) | 
                                          (User.phone == phone)).first()
        if existing_user:
            flash('El nombre de usuario, correo electrónico o número de teléfono ya existe.')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, phone=phone, password=hashed_password, type='client')
        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Ruta principal
@app.route('/')
@login_required
def index():
    return render_template('index.html', user_type=current_user.type)

# Página de impresión
@app.route('/impresion', methods=['GET', 'POST'])
@login_required
def impresion():
    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo and archivo.filename.endswith('.pdf'):
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            color = request.form['color']
            faz = request.form['faz']
            
            # Guardar la solicitud en la base de datos
            new_print = PrintRequest(filename=filename, color=color, faz=faz, user_id=current_user.id)
            db.session.add(new_print)
            db.session.commit()
            flash('Solicitud de impresión enviada exitosamente.')
            return redirect(url_for('index'))
        else:
            flash('Por favor, sube un archivo PDF válido.')
    
    return render_template('impresion.html')

# Página de servicio técnico
@app.route('/servicio', methods=['GET', 'POST'])
@login_required
def servicio():
    if request.method == 'POST':
        dispositivo = request.form['dispositivo']
        descripcion = request.form['descripcion']
        
        # Guardar la solicitud en la base de datos
        new_service = ServiceRequest(device_name=dispositivo, description=descripcion, user_id=current_user.id)
        db.session.add(new_service)
        db.session.commit()
        flash('Solicitud de servicio técnico enviada exitosamente.')
        return redirect(url_for('index'))
    
    return render_template('servicio.html')

# Página de administración
@app.route('/admin')
@login_required
def admin():
    if current_user.type != 'admin':
        flash('No tienes permisos para acceder a esta página.')
        return redirect(url_for('index'))
    
    # Obtener todas las solicitudes de impresión y servicio técnico
    print_requests = PrintRequest.query.all()
    service_requests = ServiceRequest.query.all()
    
    return render_template('admin.html', print_requests=print_requests, service_requests=service_requests)

# Ruta de cierre de sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", default=5000))
