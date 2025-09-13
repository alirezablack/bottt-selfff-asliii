# app.py
from flask import Flask
import requests
import time
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Telegram Bot is alive on Render! ✅"

def keep_alive():
    # ⚠️ حتماً این URL رو با URL واقعی رباتت جایگزین کن!
    url = "شومبول"  # ← اینجا رو عوض کن!
    while True:
        try:
            response = requests.get(url, timeout=10)
            print(f"🔄 Keep-alive ping sent: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Keep-alive error: {e}")
        time.sleep(300)  # هر 5 دقیقه یکبار

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)