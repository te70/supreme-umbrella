import requests, time, random, string
from concurrent.futures import ThreadPoolExecutor

# Use Docker service names
ENCRYPT_URL = "http://key-service:8000/encrypt"
DECRYPT_URL = "http://session-service:8000/decrypt"

for i in range(10):
    try:
        res = requests.get(ENCRYPT_URL)
        break
    except requests.exceptions.ConnectionError:
        print("Key-service not ready, retrying...")
        time.sleep(2)

def random_text(length=32):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def encrypt_message(msg):
    try:
        res = requests.post(ENCRYPT_URL, json={"message": msg})
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("Encryption error:", e)
        return None

def decrypt_message(cipher_payload):
    try:
        res = requests.post(DECRYPT_URL, json=cipher_payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("Decryption error:", e)
        return None

def encrypt_decrypt_cycle(i):
    msg = random_text(64)
    enc = encrypt_message(msg)
    if enc:
        decrypt_message(enc)
        print(f"[{i}] Success: {msg[:8]}... → encrypted → decrypted")

if __name__ == "__main__":
    NUM_REQUESTS = 50
    MAX_WORKERS = 5
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(encrypt_decrypt_cycle, i) for i in range(NUM_REQUESTS)]
        for f in futures:
            f.result()