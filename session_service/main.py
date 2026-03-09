from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64, os, time
from prometheus_client import Histogram, Counter, generate_latest
from fastapi.responses import Response

app = FastAPI()

origins = {
    "http://localhost:5173",  # Adjust this to your frontend URL
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity; adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods; adjust as needed
    allow_headers=["*"],  # Allow all headers; adjust as needed
)

decrypt_requests = Counter("decrypt_requests_total", "Total decrypt requests")
decryption_time = Histogram("decryption_time_seconds", "Time spent decrypting messages")
crypto_processing_time = Histogram("crypto_processing_seconds", "Time spent performing decryption")

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
    
    decrypt_requests.inc()  # Increment decryption request counter

    ciphertext = base64.b64decode(msg.ciphertext)
    enc_aes_key = base64.b64decode(msg.enc_aes_key)
    nonce = base64.b64decode(msg.nonce)
    tag = base64.b64decode(msg.tag)

    cipher_rsa = PKCS1_OAEP.new(private_key)

    with crypto_processing_time.time():  # Measure total decryption processing time
        aes_key = cipher_rsa.decrypt(enc_aes_key)
        dec_start = time.time()  # Start timing decryption
        cipher_aes = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher_aes.decrypt_and_verify(ciphertext, tag)

        decryption_time.observe(time.time() - dec_start)  # Record decryption duration
        
        return {"plaintext": plaintext.decode()}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")