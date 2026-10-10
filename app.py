"""Mercado Aprende: ejemplo educativo independiente de Team Alpha.
Lee los comentarios de arriba hacia abajo: petición -> validación -> SQL -> HTML.
"""
import os
import secrets
import sqlite3
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

CATEGORIES = ('Electrónica', 'Hogar', 'Libros', 'Deportes', 'Otros')
CONDITIONS = ('Nuevo', 'Como nuevo', 'Usado')


def create_app(test_config=None):
    """Una fábrica permite crear una app normal y otra aislada para pruebas."""
    app = Flask(__name__)
    Path(app.instance_path).mkdir(exist_ok=True)
    # La clave firma las cookies. En desarrollo generamos una sin guardarla en Git.
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
                      DATABASE=str(Path(app.instance_path) / 'market.db'),
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                      MAX_CONTENT_LENGTH=32 * 1024)
    if test_config:
        app.config.update(test_config)

    def db():
        """Una conexión por petición; Row permite acceder a columnas por nombre."""
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
            g.db.execute('PRAGMA foreign_keys = ON')
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop('db', None)
        if connection:
            connection.close()

    # Las tablas se crean al construir la app, también si se usa flask run.
    with app.app_context():
        db().executescript('''
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS listings (
          id INTEGER PRIMARY KEY, seller INTEGER NOT NULL REFERENCES users(id),
          title TEXT NOT NULL, category TEXT NOT NULL, condition TEXT NOT NULL,
          cents INTEGER NOT NULL CHECK(cents > 0), description TEXT NOT NULL,
          buyer INTEGER REFERENCES users(id), created TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')
        db().commit()

    def csrf_token():
        """El token impide enviar formularios desde otro sitio usando tu sesión."""
        if 'csrf' not in session:
            session['csrf'] = secrets.token_hex(32)
        return session['csrf']

    app.jinja_env.globals.update(csrf_token=csrf_token)

    @app.before_request
    def load_user_and_protect_forms():
        g.user = db().execute('SELECT * FROM users WHERE id=?',
                              (session.get('user_id'),)).fetchone()
        if request.method == 'POST':
            expected = session.get('csrf', '')
            supplied = request.form.get('csrf', '')
            if not expected or not secrets.compare_digest(expected, supplied):
                abort(400, 'Formulario expirado. Recarga la página.')

    def login_required(view):
        """Decorador: protege una ruta sin repetir el mismo código."""
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not g.user:
                flash('Inicia sesión para continuar.')
                return redirect(url_for('login'))
            return view(*args, **kwargs)
        return wrapped

    @app.route('/')
    def index():
        # Los parámetros ? evitan inyección SQL; nunca concatenamos entrada a SQL.
        query = request.args.get('q', '').strip()[:100]
        category = request.args.get('category', '')
        items = db().execute('''SELECT listings.*, users.username FROM listings
            JOIN users ON seller=users.id WHERE buyer IS NULL AND title LIKE ?
            AND (?='' OR category=?) ORDER BY listings.id DESC''',
            ('%' + query + '%', category, category)).fetchall()
        return render_template('index.html', items=items, categories=CATEGORIES,
                               query=query, category=category)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            if not 3 <= len(username) <= 30 or not 8 <= len(password) <= 128:
                flash('Usuario: 3-30 caracteres. Contraseña: 8-128 caracteres.')
            else:
                try:
                    # Guardamos un hash: la contraseña original no se almacena.
                    db().execute('INSERT INTO users(username,password) VALUES (?,?)',
                                 (username, generate_password_hash(password)))
                    db().commit()
                    flash('Cuenta creada. Ahora inicia sesión.')
                    return redirect(url_for('login'))
                except sqlite3.IntegrityError:
                    flash('Ese nombre de usuario ya existe.')
        return render_template('auth.html', registering=True)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = db().execute('SELECT * FROM users WHERE username=?',
                               (request.form.get('username', '').strip(),)).fetchone()
            if user and check_password_hash(user['password'], request.form.get('password', '')):
                session.clear()  # Rotamos la sesión y el token al iniciar sesión.
                session['user_id'] = user['id']
                return redirect(url_for('index'))
            flash('Usuario o contraseña incorrectos.')
        return render_template('auth.html', registering=False)

    @app.post('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    @app.route('/sell', methods=['GET', 'POST'])
    @login_required
    def sell():
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '')
            condition = request.form.get('condition', '')
            description = request.form.get('description', '').strip()
            try:
                # Decimal evita errores de coma flotante. Guardamos centavos enteros.
                price = Decimal(request.form.get('price', ''))
                if not price.is_finite() or not Decimal('0.01') <= price <= Decimal('1000000'):
                    raise ValueError()
                if price != price.quantize(Decimal('0.01')):
                    raise ValueError()
                cents = int(price * 100)
                if not 3 <= len(title) <= 80 or not 5 <= len(description) <= 1500:
                    raise ValueError()
                if category not in CATEGORIES or condition not in CONDITIONS:
                    raise ValueError()
            except (InvalidOperation, ValueError):
                flash('Revisa los campos: título 3-80, descripción 5-1500 y precio positivo con máximo 2 decimales.')
                return render_template('sell.html', categories=CATEGORIES, conditions=CONDITIONS), 400
            db().execute('''INSERT INTO listings(seller,title,category,condition,cents,description)
                         VALUES (?,?,?,?,?,?)''',
                         (g.user['id'], title, category, condition, cents, description))
            db().commit()
            flash('Tu producto ya está publicado.')
            return redirect(url_for('index'))
        return render_template('sell.html', categories=CATEGORIES, conditions=CONDITIONS)

    @app.get('/items/<int:item_id>')
    def detail(item_id):
        item = db().execute('''SELECT listings.*, users.username FROM listings
             JOIN users ON seller=users.id WHERE listings.id=?''', (item_id,)).fetchone()
        if not item:
            abort(404)
        return render_template('detail.html', item=item)

    @app.post('/items/<int:item_id>/buy')
    @login_required
    def buy(item_id):
        # UPDATE condicional es atómico: dos compradores no pueden comprar el mismo artículo.
        result = db().execute('''UPDATE listings SET buyer=?
                    WHERE id=? AND buyer IS NULL AND seller != ?''',
                    (g.user['id'], item_id, g.user['id']))
        db().commit()
        if result.rowcount != 1:
            abort(409, 'Producto no disponible o pertenece a tu cuenta.')
        flash('Compra simulada registrada. No se cobró dinero.')
        return redirect(url_for('account'))

    @app.get('/account')
    @login_required
    def account():
        purchases = db().execute('SELECT * FROM listings WHERE buyer=? ORDER BY id DESC',
                                 (g.user['id'],)).fetchall()
        sales = db().execute('SELECT * FROM listings WHERE seller=? ORDER BY id DESC',
                             (g.user['id'],)).fetchall()
        return render_template('account.html', purchases=purchases, sales=sales)

    return app


if __name__ == '__main__':
    # Solo localhost; no activamos el depurador para no exponer información.
    create_app().run(host='127.0.0.1', port=5000)
