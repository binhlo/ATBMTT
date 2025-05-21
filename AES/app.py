from flask import Flask, request, render_template, redirect, url_for, send_file, flash
import os
from aes_utils import aes_encrypt, aes_decrypt

app = Flask(__name__)
app.secret_key = 'super_secret_key'

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        password = request.form.get('password')
        action = request.form.get('action')

        if not file or not password:
            flash("Vui lòng chọn file và nhập mật khẩu.")
            return redirect(url_for('index'))

        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        with open(filepath, 'rb') as f:
            file_data = f.read()

        try:
            if action == 'encrypt':
                result = aes_encrypt(file_data, password)
                out_filename = 'encrypted_' + filename
            elif action == 'decrypt':
                result = aes_decrypt(file_data, password)
                out_filename = 'decrypted_' + filename
            else:
                flash("Hành động không hợp lệ.")
                return redirect(url_for('index'))

            out_path = os.path.join(PROCESSED_FOLDER, out_filename)
            with open(out_path, 'wb') as f:
                f.write(result)

            return render_template('index.html', download_filename=out_filename)

        except Exception as e:
            flash(f'Đã xảy ra lỗi: {str(e)}')
            return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        flash("File không tồn tại.")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
