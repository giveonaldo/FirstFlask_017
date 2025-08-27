
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = 'siswa.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
with get_db_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS Siswa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        Tempat TEXT NOT NULL,
        NIM TEXT NOT NULL,
        Usia INTEGER NOT NULL
    )''')
    conn.commit()

@app.route('/')
def index():
    conn = get_db_connection()
    siswa = conn.execute('SELECT * FROM Siswa').fetchall()
    conn.close()
    return render_template('index.html', siswa=siswa)


# Route to show add.html form
@app.route('/add', methods=['GET', 'POST'])
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

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
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

@app.route('/delete/<int:id>', methods=['POST'])
def delete_siswa(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Siswa WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
