from flask import Flask, request, render_template, send_file
from des import encrypt, decrypt
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    key = request.form['key']
    mode = request.form['mode']

    if not file or len(key) != 8:
        return "File or key error", 400

    content = file.read().decode('utf-8')

    if mode == 'encrypt':
        result = encrypt(content, key)
    else:
        result = decrypt(content, key)

    output_path = 'static/result.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)

    return render_template('index.html', download=True)

@app.route('/download')
def download():
    return send_file('static/result.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
