# session_service/main.py
from fastapi import FastAPI, HTTPException
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64, redis, os

app = FastAPI()
r = redis.Redis( host=os.environ.get("REDIS_HOST", "redis"), port=int(os.environ.get("REDIS_PORT", 6379)), db=0 )

KEY_PATH = os.environ.get("KEY_PATH", "/app/keys/session_rsa.pem") 
def load_or_create_rsa(): 
    if os.path.exists(KEY_PATH): 
        with open(KEY_PATH, "rb") as f: 
            return RSA.import_key(f.read()) 
    else: 
        key = RSA.generate(2048) 
        os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True) 
        with open(KEY_PATH, "wb") as f: 
            f.write(key.export_key()) 
        return key
    
rsa_key = load_or_create_rsa()
cipher_rsa = PKCS1_OAEP.new(rsa_key)

@app.post("/exchange")
def exchange(enc_session_key: str, client_id: str):
    try:
        enc = base64.b64decode(enc_session_key)
        session_key = cipher_rsa.decrypt(enc)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid encrypted session key")
    r.set(f"session:{client_id}", base64.b64encode(session_key))
    return {"status": "ok"}
