# metrics_service/main.py
from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

app = FastAPI()

# Define Prometheus metrics
ENCRYPTION_TIME = Histogram("encryption_time_seconds", "Time taken for encryption operations")
DECRYPTION_TIME = Histogram("decryption_time_seconds", "Time taken for decryption operations")
KEY_STRENGTH = Gauge("rsa_key_strength_bits", "RSA key strength in bits")
COMPUTATIONAL_OVERHEAD = Histogram("computational_overhead_seconds", "Extra overhead in crypto operations")
REQUEST_COUNT = Counter("crypto_requests_total", "Total number of crypto requests")

# Example: set key strength once (assuming RSA 2048)
KEY_STRENGTH.set(2048)

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    REQUEST_COUNT.inc()
    start_time = time.time()
    response = await call_next(request)
    overhead = time.time() - start_time
    COMPUTATIONAL_OVERHEAD.observe(overhead)
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    return {"status": "ok"}

# Example endpoints to simulate crypto operations
@app.get("/encrypt")
def encrypt():
    start = time.time()
    # simulate encryption
    time.sleep(0.05)
    ENCRYPTION_TIME.observe(time.time() - start)
    return {"status": "encrypted"}

@app.get("/decrypt")
def decrypt():
    start = time.time()
    # simulate decryption
    time.sleep(0.07)
    DECRYPTION_TIME.observe(time.time() - start)
    return {"status": "decrypted"}
