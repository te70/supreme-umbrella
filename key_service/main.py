# encrypt_api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64, os, time
from prometheus_client import Histogram, Counter, Gauge, generate_latest
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

#prometheus metrics
encrypt_requests = Counter("encrypt_requests_total", "Total encryption requests")
encryption_time = Histogram("encryption_time_seconds", "Encryption duration")
crypto_processing_time = Histogram("crypto_processing_seconds", "Time spent performing encryption")

rsa_key_strength = Gauge("rsa_key_strength_bits", "RSA key strength")
aes_key_strength = Gauge("aes_key_strength_bits", "AES key strength")

# Load RSA public key (mounted via Docker volume)
key_path = os.environ.get("PUBLIC_KEY_PATH", "/app/keys/public.pem")
with open(key_path, "rb") as f:
    recipient_pub_key = RSA.import_key(f.read())

class Message(BaseModel):
    message: str

@app.post("/encrypt")
def encrypt_message(msg: Message):
    encrypt_requests.inc()  # Increment encryption request counter

    with crypto_processing_time.time():  # Measure total encryption processing time
        # Generate AES session key
        aes_key = get_random_bytes(32)
        aes_key_strength.set(256)  # 256-bit AES

        # Encrypt message with AES-GCM
        enc_start = time.time()  # Start timing encryption
        cipher_aes = AES.new(aes_key, AES.MODE_GCM)
        ciphertext, tag = cipher_aes.encrypt_and_digest(msg.message.encode())
        encryption_time.observe(time.time() - enc_start)  # Record encryption duration

        # Encrypt AES key with RSA
        cipher_rsa = PKCS1_OAEP.new(recipient_pub_key)
        enc_aes_key = cipher_rsa.encrypt(aes_key)

        rsa_key_strength.set(recipient_pub_key.size_in_bits())  # Set RSA key strength
        
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "enc_aes_key": base64.b64encode(enc_aes_key).decode(),
            "nonce": base64.b64encode(cipher_aes.nonce).decode(),
            "tag": base64.b64encode(tag).decode()
        }

@app.get("/metrics")
def metrics():
    """
    Expose Prometheus metrics.
    """
    return Response(generate_latest(), media_type="text/plain")