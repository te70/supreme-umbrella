# encrypt_api/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
import os

app = FastAPI()

# Load RSA public key (mounted via Docker volume)
key_path = os.environ.get("PUBLIC_KEY_PATH", "/app/keys/public.pem")
with open(key_path, "rb") as f:
    recipient_pub_key = RSA.import_key(f.read())

class Message(BaseModel):
    message: str

@app.post("/encrypt")
def encrypt_message(msg: Message):
    # 1️⃣ Generate AES session key
    aes_key = get_random_bytes(32)  # 256-bit AES

    # 2️⃣ Encrypt message with AES-GCM
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)
    ciphertext, tag = cipher_aes.encrypt_and_digest(msg.message.encode())

    # 3️⃣ Encrypt AES key with RSA
    cipher_rsa = PKCS1_OAEP.new(recipient_pub_key)
    enc_aes_key = cipher_rsa.encrypt(aes_key)

    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "enc_aes_key": base64.b64encode(enc_aes_key).decode(),
        "nonce": base64.b64encode(cipher_aes.nonce).decode(),
        "tag": base64.b64encode(tag).decode()
    }