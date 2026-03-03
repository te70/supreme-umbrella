from fastapi import FastAPI
from pydantic import BaseModel
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64
import os

app = FastAPI()

key_path = os.environ.get("PRIVATE_KEY_PATH", "/app/keys/private.pem")
with open(key_path, "rb") as f:
    private_key = RSA.import_key(f.read())

class EncryptedMessage(BaseModel):
    ciphertext: str
    enc_aes_key: str
    nonce: str
    tag: str

@app.post("/decrypt")
def decrypt_message(msg: EncryptedMessage):
    ciphertext = base64.b64decode(msg.ciphertext)
    enc_aes_key = base64.b64decode(msg.enc_aes_key)
    nonce = base64.b64decode(msg.nonce)
    tag = base64.b64decode(msg.tag)

    cipher_rsa = PKCS1_OAEP.new(private_key)
    aes_key = cipher_rsa.decrypt(enc_aes_key)

    cipher_aes = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return {"plaintext": plaintext.decode()}