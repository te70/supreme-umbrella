# metrics_service/main.py
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import psutil
import time

app = FastAPI()

# Define Prometheus metrics
REQUEST_COUNT = Counter("requests_total", "Total number of requests")
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency in seconds")
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Gauge("memory_usage_percent", "Memory usage percentage")

@app.middleware("http")
async def add_metrics(request, call_next):
    REQUEST_COUNT.inc()
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    REQUEST_LATENCY.observe(latency)
    return response

@app.get("/metrics")
def metrics():
    # Update system metrics
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    return {"status": "ok"}
