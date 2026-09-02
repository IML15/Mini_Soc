import os
import time
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

# Carga las credenciales desde el archivo .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LOG_FILE = os.getenv("LOG_FILE_PATH", "auth.log")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Error: Faltan credenciales en el archivo .env")

# Expresión regular con patrones habituales de intrusión / fuerza bruta
SUSPICIOUS_PATTERNS = re.compile(
    r"(failed password|invalid user|authentication failure|sudo: auth failure|connection refused)",
    re.IGNORECASE
)

def send_telegram_alert(log_line):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Mensaje formateado en Markdown para Telegram
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
            print(f"[✓] Alerta enviada a Telegram [{timestamp}]")
        else:
            print(f"[!] Error de Telegram API: {response.text}")
    except Exception as e:
        print(f"[!] Error de conexión de red: {e}")

def monitor_logs():
    # Crea el archivo auth.log si no existe
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "a").close()

    print("=" * 50)
    print("🛡️  MINI-SOC: Sistema de Detección Activo")
    print(f"📁 Monitoreando: {LOG_FILE}")
    print("=" * 50)

    with open(LOG_FILE, "a+") as f:
        f.seek(0, 2)  # Ir al final del fichero para solo leer eventos nuevos
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            # Si la línea coincide con algún patrón de ataque, dispara la alerta
            if SUSPICIOUS_PATTERNS.search(line):
                print(f"\n[!] Evento malicioso detectado: {line.strip()}")
                send_telegram_alert(line)

if __name__ == "__main__":
    monitor_logs()