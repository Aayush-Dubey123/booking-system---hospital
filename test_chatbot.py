import requests
import json
import time

URL_LOGIN = "http://localhost:8000/v1/users/login"
URL_CHAT = "http://localhost:8000/v1/chat"
URL_STREAM = "http://localhost:8000/v1/chat/stream"

print("================= LOGIN =================")
login_res = requests.post(URL_LOGIN, json={"email": "patient1@example.com", "password": "password123"})
if login_res.status_code != 200:
    print(f"Login failed: {login_res.status_code} - {login_res.text}")
    print("Please create a patient account or use an existing one in the UI.")
    exit(1)

TOKEN = login_res.json().get("access_token")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
print("Login successful.")

print("\n================= TEST SCENARIOS =================")

def chat(cid, msg):
    print(f"\n[Patient]: {msg}")
    res = requests.post(URL_CHAT, headers=HEADERS, json={"conversation_id": cid, "user_input": msg})
    if res.status_code == 200:
        print(f"[Assistant]: {res.json().get('response')}")
    else:
        print(f"[ERROR]: {res.status_code} - {res.text}")

chat("test-normal", "Hello! Who are you?")
chat("test-my-appts", "What appointments do I have?")
chat("test-slots", "Show me available slots tomorrow.")
chat("test-book", "Book me tomorrow at 10:00.")
chat("test-book", "I need it for a checkup. I have a headache. My temperature is 37.1. The hospital ID is 6a7720e5dc98aabdfda4a0c6.")
chat("test-invalid", "Book me tomorrow at 02:00. Reason: checkup, symptoms: none, temperature: 37, hospital_id: 6a7720e5dc98aabdfda4a0c6.")

print("\n[Patient]: (Streaming) Tell me a short joke about doctors.")
res = requests.post(URL_STREAM, headers=HEADERS, json={"conversation_id": "test-stream", "user_input": "Tell me a short joke about doctors."}, stream=True)
print("[Assistant]: ", end="", flush=True)
for line in res.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data = json.loads(line_str[6:])
            if 'text' in data:
                print(data['text'], end="", flush=True)
print("\n")
