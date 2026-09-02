import os
import time
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

# Load the credentials from the file .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LOG_FILE = os.getenv("LOG_FILE_PATH", "auth.log")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Fail: Credentials are missing from the file .env")

# Regular expressions that can become intrusions in our system
SUSPICIOUS_PATTERNS = re.compile(
    r"(failed password|invalid user|authentication failure|sudo: auth failure|connection refused)",
    re.IGNORECASE
)

def send_telegram_alert(log_line):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Telegram Bot's message
    message = (
        "🚨 *[MINI-SOC] INTRUSION DETECTED*\n\n"
        f"📅 *Timestamp:* `{timestamp}`\n"
        f"🔍 *Severity:* `HIGH`\n"
        f"📄 *Log Event:*\n`{log_line.strip()}`"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"[✓] Alert sent to Telegram [{timestamp}]")
        else:
            print(f"[!] Error from Telegram's API: {response.text}")
    except Exception as e:
        print(f"[!] Conexion failed: {e}")

def monitor_logs():
    # Create the auth.log file if it does not exist
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "a").close()

    print("=" * 50)
    print("🛡️  MINI-SOC: Active Detection System")
    print(f"📁 Monitoring: {LOG_FILE}")
    print("=" * 50)

    with open(LOG_FILE, "a+") as f:
        f.seek(0, 2)  # Go to the end of the file to read only new events
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            # If the line matches an attack pattern, trigger the alert
            if SUSPICIOUS_PATTERNS.search(line):
                print(f"\n[!] Malicious event detected: {line.strip()}")
                send_telegram_alert(line)

if __name__ == "__main__":
    monitor_logs()