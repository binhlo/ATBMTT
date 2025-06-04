import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, g
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DATABASE = 'users.db'

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------- DATABASE ------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        # Tạo bảng files với cột sha256
        db.execute('''CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            filename TEXT NOT NULL,
            sha256 TEXT
        )''')
        db.commit()

init_db()

# ---------- AUTH ------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashpass = generate_password_hash(password)
        try:
            db = get_db()
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashpass))
            db.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Tên tài khoản đã tồn tại!')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE username=?', [username], one=True)
        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Sai tài khoản hoặc mật khẩu!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ---------- MAIN ------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db()
    users = [u[0] for u in query_db('SELECT username FROM users WHERE username != ?', [session['username']])]
    if request.method == 'POST':
        receiver = request.form['receiver']
        file = request.files['file']
        if not file or file.filename == '':
            flash('Vui lòng chọn file!')
            return redirect(url_for('index'))
        filename = f"{session['username']}_to_{receiver}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Tính SHA-256
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        file_hash = sha256_hash.hexdigest()

        db.execute('INSERT INTO files (sender, receiver, filename, sha256) VALUES (?, ?, ?, ?)',
                   (session['username'], receiver, filename, file_hash))
        db.commit()
        flash(f'Đã gửi file thành công! SHA-256: {file_hash}')
    # Lấy danh sách file gửi cho mình
    files = query_db('SELECT sender, filename, sha256 FROM files WHERE receiver=?', [session['username']])
    return render_template('index.html', users=users, files=files, username=session['username'])

@app.route('/download/<filename>')
def download(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    # Kiểm tra quyền tải file
    file_record = query_db('SELECT receiver FROM files WHERE filename=?', [filename], one=True)
    if file_record and file_record[0] == session['username']:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        flash('Bạn không có quyền tải file này!')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
