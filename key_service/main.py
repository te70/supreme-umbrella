from fastapi import FastAPI
import os
from Crypto.PublicKey import RSA

app = FastAPI()

KEY_PATH = os.environ.get("KEY_PATH", "/app/keys/server_rsa.pem")

def load_or_create_rsa():
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            key = RSA.import_key(f.read())
    else:
        key = RSA.generate(2048)
        os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
        with open(KEY_PATH, "wb") as f:
            f.write(key.export_key())
    return key

rsa_key = load_or_create_rsa()
public_key = rsa_key.publickey().export_key().decode()

@app.get("/public_key")
def get_public_key():
    return {"public_key": public_key}
