# key_service/main.py
from fastapi import FastAPI
from Crypto.PublicKey import RSA

app = FastAPI()
rsa_key = RSA.generate(2048)
public_key = rsa_key.publickey().export_key().decode()

@app.get("/public_key")
def get_public_key():
    return {"public_key": public_key}
