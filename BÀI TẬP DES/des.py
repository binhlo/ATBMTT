from bitarray import bitarray

# --- Các hàm hỗ trợ ---
def text_to_bin(text):
    """Chuyển đổi văn bản thành chuỗi nhị phân."""
    return ''.join(format(ord(c), '08b') for c in text)

def bin_to_text(binary):
    """Chuyển đổi chuỗi nhị phân thành văn bản."""
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def pad_binary(binary):
    """Padding dữ liệu cho độ dài bội số của 64 bits."""
    pad_len = 64 - (len(binary) % 64)
    return binary + ('0' * (pad_len if pad_len != 64 else 0))

def xor(a, b):
    """XOR hai chuỗi nhị phân."""
    return ''.join('1' if i != j else '0' for i, j in zip(a, b))

def shift_left(key_chunk, n):
    """Dịch trái chuỗi nhị phân theo số bit n."""
    return key_chunk[n:] + key_chunk[:n]

# --- Bảng hoán vị ---
IP = [58,50,42,34,26,18,10,2, 60,52,44,36,28,20,12,4, 62,54,46,38,30,22,14,6, 64,56,48,40,32,24,16,8,
      57,49,41,33,25,17,9,1, 59,51,43,35,27,19,11,3, 61,53,45,37,29,21,13,5, 63,55,47,39,31,23,15,7]
IP_INV = [40,8,48,16,56,24,64,32, 39,7,47,15,55,23,63,31, 38,6,46,14,54,22,62,30, 37,5,45,13,53,21,61,29,
          36,4,44,12,52,20,60,28, 35,3,43,11,51,19,59,27, 34,2,42,10,50,18,58,26, 33,1,41,9,49,17,57,25]
E = [32,1,2,3,4,5,4,5,6,7,8,9,8,9,10,11,12,13,12,13,14,15,16,17,16,17,18,19,20,21,20,21,22,23,24,25,24,25,26,27,28,29,28,29,30,31,32,1]
P = [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25]
S_BOXES = [
    [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7], [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
     [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0], [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],

    [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10], [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
     [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15], [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],

    [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8], [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
     [13,6,9,0,12,11,7,3,15,1,2,10,5,8,14,4], [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],

    [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15], [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
     [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4], [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],

    [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9], [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
     [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14], [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],

    [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11], [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
     [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6], [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],

    [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1], [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
     [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2], [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],

    [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7], [1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],
     [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8], [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]],
]

PC1 = [57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,
       60,52,44,36,63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,
       29,21,13,5,28,20,12,4]
PC2 = [14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,
       41,52,31,37,47,55,30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32]
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

def generate_keys(key):
    key_bin = text_to_bin(key)
    key_bin = ''.join(key_bin[i-1] for i in PC1)  # Hoán vị PC1
    left, right = key_bin[:28], key_bin[28:]
    keys = []
    for shift in SHIFTS:
        left, right = shift_left(left, shift), shift_left(right, shift)
        combined = left + right
        round_key = ''.join(combined[i-1] for i in PC2)  # Hoán vị PC2
        keys.append(round_key)
    return keys

def s_box_substitution(block):
    """Thay thế bằng S-box."""
    output = ''
    for i in range(8):
        chunk = block[i*6:(i+1)*6]
        row = int(chunk[0] + chunk[5], 2)
        col = int(chunk[1:5], 2)
        val = S_BOXES[i][row][col]
        output += format(val, '04b')
    return output

def des_round(left, right, key):
    """Một vòng mã hóa DES."""
    expanded = ''.join(right[i-1] for i in E)  # Mở rộng
    xored = xor(expanded, key)  # XOR
    sboxed = s_box_substitution(xored)  # Thay thế bằng S-box
    permuted = ''.join(sboxed[i-1] for i in P)  # Hoán vị
    return xor(left, permuted), right

def des_encrypt_block(block, keys):
    """Mã hóa một block 64-bit."""
    block = ''.join(block[i-1] for i in IP)  # Hoán vị IP
    left, right = block[:32], block[32:]
    for key in keys:
        left, right = des_round(left, right, key)
        left, right = right, left
    combined = right + left
    return ''.join(combined[i-1] for i in IP_INV)  # Hoán vị IP_INV

def des(text, key, mode='encrypt'):
    """Thuật toán DES chung (mã hóa và giải mã)."""
    keys = generate_keys(key)
    if mode == 'decrypt':
        keys = keys[::-1]  # Đảo ngược key khi giải mã
    binary = pad_binary(text_to_bin(text))
    result = ''
    for i in range(0, len(binary), 64):
        block = binary[i:i+64]
        result += des_encrypt_block(block, keys)
    return bin_to_text(result)

def encrypt(text, key): return des(text, key, 'encrypt')
def decrypt(text, key): return des(text, key, 'decrypt')
