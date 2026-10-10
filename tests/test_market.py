"""Pruebas reproducibles: cada prueba usa una base temporal independiente."""
import re
import sqlite3
import pytest
from app import create_app

@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING': True, 'SECRET_KEY': 'testing-only',
                       'DATABASE': str(tmp_path / 'test.db')})

def post(client, path, data=None):
    # El test utiliza el token real; no desactivamos CSRF para facilitar las pruebas.
    client.get('/login')
    with client.session_transaction() as session:
        token = session['csrf']
    return client.post(path, data={**(data or {}), 'csrf': token}, follow_redirects=False)

def register(client, username):
    return post(client, '/register', {'username': username, 'password': 'practice123'})

def login(client, username):
    return post(client, '/login', {'username': username, 'password': 'practice123'})

def listing(client, **changes):
    data = {'title': 'Bicicleta azul', 'category': 'Deportes', 'condition': 'Usado',
            'price': '125.50', 'description': 'Bicicleta en buen estado.'}
    return post(client, '/sell', {**data, **changes})

def test_full_purchase_flow_and_double_purchase(app):
    seller, buyer = app.test_client(), app.test_client()
    register(seller, 'vendedor'); login(seller, 'vendedor')
    assert listing(seller).status_code == 302
    assert b'Bicicleta azul' in seller.get('/').data
    assert post(seller, '/items/1/buy').status_code == 409
    register(buyer, 'comprador'); login(buyer, 'comprador')
    assert post(buyer, '/items/1/buy').status_code == 302
    assert post(buyer, '/items/1/buy').status_code == 409
    assert b'Bicicleta azul' in buyer.get('/account').data
    assert b'Bicicleta azul' not in buyer.get('/').data
    assert b'Vendido' in seller.get('/account').data

@pytest.mark.parametrize('price', ['abc', '-1', '0', 'NaN', 'Infinity', '1.001', '1000001'])
def test_bad_price(app, price):
    client = app.test_client(); register(client, 'vendedor'); login(client, 'vendedor')
    assert listing(client, price=price).status_code == 400
    with sqlite3.connect(app.config['DATABASE']) as connection:
        assert connection.execute('SELECT COUNT(*) FROM listings').fetchone()[0] == 0

def test_auth_csrf_and_password_hash(app):
    client = app.test_client()
    assert client.get('/sell').status_code == 302
    assert client.post('/register', data={'username': 'test'}).status_code == 400
    assert register(client, 'usuario').status_code == 302
    assert register(client, 'usuario').status_code == 200
    assert post(client, '/login', {'username':'usuario', 'password':'wrong'}).status_code == 200
    assert login(client, 'usuario').status_code == 302
    with sqlite3.connect(app.config['DATABASE']) as connection:
        assert connection.execute('SELECT password FROM users').fetchone()[0] != 'practice123'
    post(client, '/logout')
    assert client.get('/account').status_code == 302

def test_search_escape_missing_and_categories(app):
    client = app.test_client(); register(client, 'vendedor'); login(client, 'vendedor')
    assert listing(client, title='<script>alert(1)</script>').status_code == 302
    assert b'&lt;script&gt;' in client.get('/').data
    assert b'<script>alert(1)</script>' not in client.get('/').data
    assert b'&lt;script&gt;' not in client.get('/?q=unknown').data
    assert listing(client, category='invalid').status_code == 400
    assert listing(client, condition='invalid').status_code == 400
    assert client.get('/items/999').status_code == 404
    assert client.get('/?category=Libros').status_code == 200
