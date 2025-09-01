
# Guest only decorator
def guest_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random value
# Middleware decorator for authentication
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
DATABASE = 'siswa.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if not exists
with get_db_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS Siswa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        Tempat TEXT NOT NULL,
        NIM TEXT NOT NULL,
        Usia INTEGER NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    conn.commit()
    
# Register route
@app.route('/register', methods=['GET', 'POST'])
@guest_only
def register():
    error = None
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO User (nama, email, password) VALUES (?, ?, ?)',
                         (nama, email, password))
            conn.commit()
            user = conn.execute('SELECT * FROM User WHERE email = ?', (email,)).fetchone()
            conn.close()
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_nama'] = user['nama']
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            error = 'Email sudah terdaftar.'
            conn.close()
    return render_template('register.html', error=error)

# Home
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    siswa = conn.execute('SELECT * FROM Siswa').fetchall()
    conn.close()
    return render_template('index.html', siswa=siswa)


# Route to show add.html form
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_html():
    if request.method == 'POST':
        nama = request.form['nama']
        Tempat = request.form['Tempat']
        NIM = request.form['NIM']
        Usia = request.form['Usia']
        conn = get_db_connection()
        conn.execute('INSERT INTO Siswa (nama, Tempat, NIM, Usia) VALUES (?, ?, ?, ?)',
                     (nama, Tempat, NIM, Usia))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

# Edit
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_siswa(id):
    conn = get_db_connection()
    siswa = conn.execute('SELECT * FROM Siswa WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        nama = request.form['nama']
        Tempat = request.form['Tempat']
        NIM = request.form['NIM']
        Usia = request.form['Usia']
        conn.execute('UPDATE Siswa SET nama = ?, Tempat = ?, NIM = ?, Usia = ? WHERE id = ?',
                     (nama, Tempat, NIM, Usia, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return render_template('edit.html', siswa=siswa)

# Delete
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_siswa(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Siswa WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
@guest_only
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM User WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user is None:
            error = 'Email tidak ditemukan.'
        elif user['password'] != password:
            error = 'Password anda salah.'
        else:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_nama'] = user['nama']
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

# Logout route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
