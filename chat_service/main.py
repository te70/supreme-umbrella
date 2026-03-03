# chat_service/main.py
from fastapi import FastAPI, WebSocket
import redis, base64, json
from Crypto.Cipher import AES

app = FastAPI()
r = redis.Redis()

@app.websocket("/ws/{client_id}")
async def chat(websocket: WebSocket, client_id: str):
    await websocket.accept()
    session_key = base64.b64decode(r.get(f"session:{client_id}"))
    while True:
        data = await websocket.receive_text()
        msg = json.loads(data)
        cipher = AES.new(session_key, AES.MODE_GCM, nonce=base64.b64decode(msg["nonce"]))
        plaintext = cipher.decrypt_and_verify(base64.b64decode(msg["ciphertext"]), base64.b64decode(msg["tag"]))
        # Echo back encrypted
        cipher_out = AES.new(session_key, AES.MODE_GCM)
        ct, tag = cipher_out.encrypt_and_digest(plaintext)
        await websocket.send_text(json.dumps({
            "nonce": base64.b64encode(cipher_out.nonce).decode(),
            "ciphertext": base64.b64encode(ct).decode(),
            "tag": base64.b64encode(tag).decode()
        }))
