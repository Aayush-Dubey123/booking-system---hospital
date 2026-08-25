import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure citycare-backend is in python path
backend_path = Path(__file__).resolve().parent.parent / "citycare-backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# pyrefly: ignore [missing-import]
from core.apis.api import app

def test_telegram_webhook_valid():
    client = TestClient(app)
    payload = {
        "update_id": 123456789,
        "message": {
            "message_id": 999,
            "from": {
                "id": 111111,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 111111,
                "type": "private",
                "username": "testuser"
            },
            "date": 1629892038,
            "text": "Hello CityCare!"
        }
    }
    response = client.post("/telegram/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["status"] == "processed"

def test_telegram_webhook_invalid():
    client = TestClient(app)
    # Missing update_id (which is required by our schema)
    payload = {
        "message": {
            "message_id": 999,
            "chat": {
                "id": 111111,
                "type": "private"
            },
            "date": 1629892038
        }
    }
    response = client.post("/telegram/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert "error" in data
    assert data["error"] == "Validation failed"

if __name__ == "__main__":
    print("Running Telegram Webhook Tests...")
    try:
        test_telegram_webhook_valid()
        print("OK: test_telegram_webhook_valid passed!")
        test_telegram_webhook_invalid()
        print("OK: test_telegram_webhook_invalid passed!")
        print("All tests passed successfully!")
    except AssertionError as e:
        print(f"Assertion error during tests: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during tests: {e}")
        sys.exit(1)
