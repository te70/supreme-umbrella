# session_service/main.py
from fastapi import FastAPI
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64, redis

app = FastAPI()
r = redis.Redis()

rsa_key = RSA.generate(2048)
cipher_rsa = PKCS1_OAEP.new(rsa_key)

@app.post("/exchange")
def exchange(enc_session_key: str, client_id: str):
    enc = base64.b64decode(enc_session_key)
    session_key = cipher_rsa.decrypt(enc)
    r.set(f"session:{client_id}", base64.b64encode(session_key))
    return {"status": "ok"}
