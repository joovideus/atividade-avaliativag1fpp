from flask import Flask, request, jsonify
import sqlite3
from flask_bcrypt import Bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'supersecretkey'

# Função para conectar ao banco de dados SQLite
def connect_db():
    return sqlite3.connect('data.db')

# Função para criar as tabelas se não existirem
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()

# Inicializa as tabelas ao iniciar o aplicativo
create_tables()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')

    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except:
        return jsonify({'message': 'Username already exists!'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user[2], password):
        token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401

@app.route('/data', methods=['POST', 'GET'])
@token_required
def use_api(current_user):
    try:
        if request.method == "POST":
            value = request.json.get('data')
            if value is None:
                return jsonify({"error": "No value provided"}), 400
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO data (value) VALUES (?)', (value,))
                conn.commit()
            return jsonify({"message": "Value added successfully"}), 201
        elif request.method == "GET":
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM data')
                rows = cursor.fetchall()
            values = [{"id": row[0], "data": row[1]} for row in rows]
            return jsonify(values), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
