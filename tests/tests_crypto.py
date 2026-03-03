# tests/test_crypto.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def test_aes_encrypt_decrypt():
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_GCM)
    ct, tag = cipher.encrypt_and_digest(b"hello")
    cipher2 = AES.new(key, AES.MODE_GCM, nonce=cipher.nonce)
    pt = cipher2.decrypt_and_verify(ct, tag)
    assert pt == b"hello"
