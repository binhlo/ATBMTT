from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import hashlib
import os

KEY_LENGTH = 32  # 256-bit
IV_LENGTH = 16
SALT_LENGTH = 16
ITERATIONS = 100_000

def derive_key(password: str, salt: bytes) -> bytes:
    return PBKDF2(password, salt, dkLen=KEY_LENGTH, count=ITERATIONS, hmac_hash_module=hashlib.sha256)

def aes_encrypt(data: bytes, password: str) -> bytes:
    salt = get_random_bytes(SALT_LENGTH)
    iv = get_random_bytes(IV_LENGTH)
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    pad_len = 16 - len(data) % 16
    padded_data = data + bytes([pad_len] * pad_len)

    encrypted = cipher.encrypt(padded_data)
    return salt + iv + encrypted

def aes_decrypt(encrypted_data: bytes, password: str) -> bytes:
    salt = encrypted_data[:SALT_LENGTH]
    iv = encrypted_data[SALT_LENGTH:SALT_LENGTH + IV_LENGTH]
    ciphertext = encrypted_data[SALT_LENGTH + IV_LENGTH:]

    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    padded_data = cipher.decrypt(ciphertext)
    pad_len = padded_data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Sai mật khẩu hoặc dữ liệu bị lỗi.")
    return padded_data[:-pad_len]
