import os
import sys
import time
import json
import subprocess
import urllib.request
from dotenv import load_dotenv

# Set console encoding to UTF-8 to handle any unicode logging/characters cleanly
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def get_env_token():
    # Load .env file
    root_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(root_dir, ".env")
    load_dotenv(dotenv_path=env_path)
    
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file!")
        sys.exit(1)
    return token

def get_ngrok_url():
    print("⏳ Waiting for Ngrok tunnel to initialize...")
    for i in range(15):
        try:
            with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=2) as response:
                data = json.loads(response.read().decode())
                tunnels = data.get("tunnels", [])
                for tunnel in tunnels:
                    public_url = tunnel.get("public_url", "")
                    if public_url.startswith("https://"):
                        return public_url
        except Exception:
            pass
        time.sleep(1)
    return None

def set_telegram_webhook(token, public_url):
    webhook_target = f"{public_url}/telegram/webhook"
    print(f"🔗 Setting Telegram Webhook to: {webhook_target}")
    
    url = f"https://api.telegram.org/bot{token}/setWebhook"
    payload = json.dumps({"url": webhook_target}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                print("✅ Telegram Webhook registered successfully!")
                print(f"ℹ️ Response description: {result.get('description')}")
            else:
                print(f"❌ Failed to set webhook: {result}")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Error communicating with Telegram API: {e}")
        sys.exit(1)

def main():
    token = get_env_token()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Resolve venv python
    venv_python = os.path.join(root_dir, "venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = sys.executable
        print(f"⚠️ Warning: Could not find virtual environment python at venv/Scripts/python.exe, using default: {venv_python}")
    
    ngrok_proc = None
    backend_proc = None
    
    try:
        print("🚀 Starting Ngrok tunnel on port 8000...")
        # Start ngrok in background
        ngrok_proc = subprocess.Popen(
            ["ngrok", "http", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Poll for ngrok public url
        public_url = get_ngrok_url()
        if not public_url:
            print("❌ Error: Failed to retrieve Ngrok public URL. Please make sure Ngrok is installed and authorized.")
            sys.exit(1)
            
        print(f"🚀 Ngrok is up at {public_url}")
        
        # Set Telegram webhook
        set_telegram_webhook(token, public_url)
        
        # Start backend
        print("🚀 Starting CityCare backend server...")
        backend_dir = os.path.join(root_dir, "citycare-backend")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"
        backend_proc = subprocess.Popen(
            [venv_python, "main.py"],
            cwd=backend_dir,
            env=env
        )
        
        # Keep orchestrator running and monitor backend process
        backend_proc.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down backend and Ngrok...")
    finally:
        if backend_proc and backend_proc.poll() is None:
            print("Stopping backend...")
            backend_proc.terminate()
            backend_proc.wait()
        if ngrok_proc and ngrok_proc.poll() is None:
            print("Stopping Ngrok...")
            ngrok_proc.terminate()
            ngrok_proc.wait()
        print("👋 Done!")

if __name__ == "__main__":
    main()
