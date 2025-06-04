# File: aes_utils.py

import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# 1. Hàm derive key: từ chuỗi key_str → 32‐byte (256 bit) qua SHA‐256. 
#    Nếu muốn AES-128, chỉ lấy 16 byte đầu. Ở đây ta dùng AES-256:
def derive_key(key_str: str) -> bytes:
    """
    Trả về key 32 bytes từ mật khẩu key_str bằng SHA-256
    """
    hash_obj = hashlib.sha256(key_str.encode('utf-8'))
    return hash_obj.digest()  # 32 bytes

# 2. Mã hóa AES-CBC:
from typing import Tuple

def encrypt_aes(plaintext: str, key_str: str) -> Tuple[str, str]:

    """
    Input: plaintext (str), key_str (str) do user nhập.
    Output: (iv_hex, ciphertext_hex) (cả hai đều là chuỗi hex).
    """
    key = derive_key(key_str)           # 32 bytes
    iv = os.urandom(16)                 # 16 bytes IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # Với CBC, cần pad plaintext xuống bội số block (16 bytes):
    padded = pad(plaintext.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded)  # bytes
    # Trả về hex để dễ embed vào JSON:
    return iv.hex(), ciphertext.hex()

# 3. Giải mã AES-CBC:
def decrypt_aes(iv_hex: str, ciphertext_hex: str, key_str: str) -> str:
    """
    Input: iv_hex, ciphertext_hex là chuỗi hex; key_str (str).
    Output: plaintext (str). Nếu sai key hoặc giải mã lỗi, sẽ bắn exception.
    """
    key = derive_key(key_str)
    iv = bytes.fromhex(iv_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plain = cipher.decrypt(ciphertext)
    plaintext = unpad(padded_plain, AES.block_size).decode('utf-8')
    return plaintext
