# File: app.py

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some-secret-key'  # tự đặt 1 chuỗi bất kỳ
# Dùng eventlet cho socketio:
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@app.route('/')
def index():
    """
    Trả về trang index.html (ứng dụng chat).
    """
    return render_template('index.html')


# Khi nhận event 'send_message' từ client:
@socketio.on('send_message')
def handle_send_message(json_data):
    """
    Mỗi client sẽ gửi lên gói JSON dạng:
    {
        'iv': '<hex>',
        'ciphertext': '<hex>',
        'username': '<tên hiển thị>',
        'timestamp': '<timestamp tùy chọn>'
    }
    Server chỉ việc phát broadcast sang các client khác (không giải mã).
    """
    # Gửi lại cho tất cả client (bao gồm cả người gửi) dưới event 'receive_message'
    socketio.emit('receive_message', json_data, broadcast=True)


if __name__ == '__main__':
    # Chạy server trên cổng 5000, dùng eventlet:
    socketio.run(app, host='0.0.0.0', port=5000)
