// File: static/client.js

document.addEventListener("DOMContentLoaded", () => {
  // 1. Kết nối Socket.IO
  const socket = io();  // mặc định sẽ kết nối tới host/ngõ 5000

  // 2. Tham chiếu tới các phần tử DOM
  const usernameInput = document.getElementById("username");
  const keyInput = document.getElementById("keyInput");
  const messageInput = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  const messagesDiv = document.getElementById("messages");

  // 3. Hàm derive key sang 256 bit dùng CryptoJS
  function deriveKeyJS(keyStr) {
    // Dùng SHA-256 hash rồi lấy kết quả làm key (32 bytes)
    const hash = CryptoJS.SHA256(keyStr);
    return hash; // CryptoJS sử dụng WordArray, đủ dài 256-bit.
  }

  // 4. Hàm mã hóa (CryptoJS AES-CBC, padding PKCS7 mặc định)
  function encryptAES_JS(plaintext, keyStr) {
    // key là WordArray (256 bit), ta vẫn dùng AES-256
    const key = deriveKeyJS(keyStr);
    // Tạo IV ngẫu nhiên 16 bytes (CryptoJS cho phép từ hàng rào)
    const iv = CryptoJS.lib.WordArray.random(16); // 16 bytes = 128 bit
    // Mã hóa
    const encrypted = CryptoJS.AES.encrypt(plaintext, key, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    });
    // encrypted.ciphertext là WordArray; để lấy iv, ta dùng iv.toString()
    return {
      iv: iv.toString(CryptoJS.enc.Hex),
      ciphertext: encrypted.ciphertext.toString(CryptoJS.enc.Hex)
    };
  }

  // 5. Hàm giải mã
  function decryptAES_JS(ivHex, ciphertextHex, keyStr) {
    const key = deriveKeyJS(keyStr);
    const iv = CryptoJS.enc.Hex.parse(ivHex);

    // Tạo đối tượng CipherParams chứa ciphertext
    const cipherParams = CryptoJS.lib.CipherParams.create({
      ciphertext: CryptoJS.enc.Hex.parse(ciphertextHex)
    });

    // Giải mã
    try {
      const decrypted = CryptoJS.AES.decrypt(cipherParams, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
      });
      const plaintext = decrypted.toString(CryptoJS.enc.Utf8);
      if (!plaintext) {
        // Nếu kết quả rỗng, có thể padding lỗi hoặc key sai
        throw new Error("Đầu ra rỗng => key sai hoặc dữ liệu hỏng");
      }
      return plaintext;
    } catch (err) {
      // Ném ra nếu padding lỗi
      throw new Error("Giải mã không thành công");
    }
  }

  // 6. Xử lý khi người dùng bấm “Gửi”
  sendBtn.addEventListener("click", () => {
    const username = usernameInput.value.trim();
    const keyStr = keyInput.value;
    const plaintext = messageInput.value.trim();

    if (!username) {
      alert("Vui lòng nhập tên hiển thị.");
      return;
    }
    if (!keyStr) {
      alert("Vui lòng nhập mật khẩu (key).");
      return;
    }
    if (!plaintext) {
      alert("Vui lòng nhập nội dung tin nhắn.");
      return;
    }

    // Thực hiện mã hóa:
    const { iv, ciphertext } = encryptAES_JS(plaintext, keyStr);
    const timestamp = new Date().toLocaleTimeString();

    // Tạo JSON payload:
    const payload = {
      iv: iv,
      ciphertext: ciphertext,
      username: username,
      timestamp: timestamp
    };

    // Emit event 'send_message' lên server:
    socket.emit("send_message", payload);

    // Xóa ô nhập tin nhắn cho lần sau:
    messageInput.value = "";
  });

  // 7. Xử lý khi nhận tin từ server
  socket.on("receive_message", (data) => {
    // data kỳ vọng nhận về: { iv, ciphertext, username, timestamp }
    const { iv, ciphertext, username, timestamp } = data;
    const keyStr = keyInput.value;

    // Tạo thẻ hiển thị:
    const messageElement = document.createElement("div");
    messageElement.classList.add("single-message");

    // Nếu user chưa nhập key thì báo lỗi:
    if (!keyStr) {
      messageElement.innerText = `[${timestamp}] ${username}: 
        [Chưa nhập key để giải mã]`;
      messagesDiv.appendChild(messageElement);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
      return;
    }

    // Thử giải mã:
    let plaintext = "";
    try {
      plaintext = decryptAES_JS(iv, ciphertext, keyStr);
      // Hiển thị định dạng: [hh:mm:ss] username: plaintext
      messageElement.innerText = `[${timestamp}] ${username}: ${plaintext}`;
    } catch (err) {
      messageElement.innerText = `[${timestamp}] ${username}: [Không thể giải mã (key sai)]`;
    }

    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  });
});
