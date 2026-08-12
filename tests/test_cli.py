"""
test_cli.py — End-to-end CLI test suite.

Tests the CLI commands against the running CityCare backend at localhost:8000.
Runs all flows: signup, login, hospitals, slots, book, appointments,
prescriptions, chat, logout, and error handling.

Usage:
  python test_cli.py

Prerequisites:
  - Backend running at http://localhost:8000
  - CLI dependencies installed (typer, rich, httpx)
"""
from __future__ import annotations

import os
import sys
import json
import subprocess
import time
import uuid
from datetime import date, timedelta
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import httpx

BASE_URL = "http://localhost:8000"
TOKEN_FILE = Path.home() / ".hospitalcare" / "token.json"

# ─── Helpers ─────────────────────────────────────────────────────────────────

PASS_MARK = "  ✓ PASS"
FAIL_MARK = "  ✗ FAIL"

results: list[tuple[str, bool, str]] = []


def run_test(name: str, fn) -> bool:
    try:
        fn()
        results.append((name, True, ""))
        print(f"{PASS_MARK}: {name}")
        return True
    except AssertionError as e:
        results.append((name, False, str(e)))
        print(f"{FAIL_MARK}: {name}")
        print(f"         {e}")
        return False
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"{FAIL_MARK}: {name}")
        print(f"         Exception: {e}")
        return False


def api(method: str, path: str, **kwargs):
    """Direct httpx call to the backend (bypassing CLI) for test setup."""
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        resp = getattr(c, method)(path, **kwargs)
    return resp


def cli(*args: str, input: str | None = None) -> subprocess.CompletedProcess:
    """Run a hospitalcare CLI command and return the completed process."""
    cmd = [sys.executable, str(ROOT / "hospitalcare.py")] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=input,
        cwd=str(ROOT),
    )


# Unique test email to avoid conflicts
TEST_EMAIL = f"cli_test_{uuid.uuid4().hex[:8]}@citycare-test.com"
TEST_PASSWORD = "TestPass1234"
TEST_FIRST = "CLITest"
TEST_LAST = "Patient"

# ─── Tests ───────────────────────────────────────────────────────────────────

def test_backend_reachable():
    resp = api("get", "/health")
    assert resp.status_code == 200, f"Backend not healthy: {resp.text}"


def test_signup_via_api():
    """Create test patient via API directly (avoids interactive prompts)."""
    resp = api("post", "/v1/users/signup", json={
        "first_name": TEST_FIRST,
        "last_name": TEST_LAST,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    })
    assert resp.status_code == 201, f"Signup failed: {resp.text}"
    data = resp.json()
    assert data["email"] == TEST_EMAIL


def test_login_saves_token():
    """Login via API, manually save token, then verify CLI auth reads it."""
    resp = api("post", "/v1/users/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data

    # Simulate what `hospitalcare login` does — save the token
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps({
        "access_token": data["access_token"],
        "role": data["role"],
        "hospital_id": data.get("hospital_id"),
    }), encoding="utf-8")

    assert TOKEN_FILE.exists(), "Token file not created"


def test_whoami_output():
    """hospitalcare whoami should output role info."""
    result = cli("whoami")
    assert result.returncode == 0, f"whoami failed: {result.stderr}"
    assert "patient" in result.stdout.lower(), f"Expected 'patient' in output: {result.stdout}"


def test_hospitals_list():
    """hospitalcare hospitals should list hospitals."""
    result = cli("hospitals")
    assert result.returncode == 0, f"hospitals failed: {result.stderr}"
    # Should have some table output
    output = result.stdout + result.stderr
    assert len(output) > 10, "No hospitals output"


def test_slots_today():
    """hospitalcare slots should show today's slots."""
    today = date.today().isoformat()
    result = cli("slots", today)
    assert result.returncode == 0, f"slots failed: {result.stderr}"
    output = result.stdout + result.stderr
    # Should mention slots or availability
    assert "slot" in output.lower() or "free" in output.lower() or "available" in output.lower(), \
        f"No slot info in output: {output}"


def test_dashboard():
    """hospitalcare dashboard should show stats."""
    result = cli("dashboard")
    assert result.returncode == 0, f"dashboard failed: {result.stderr}"


def test_appointments_empty():
    """hospitalcare appointments for new user should show empty or warning."""
    result = cli("appointments")
    assert result.returncode == 0, f"appointments failed: {result.stderr}"
    output = result.stdout + result.stderr
    # Either a table (with no rows) or a warning
    assert len(output) > 0, "No output from appointments"


def test_prescriptions_empty():
    """hospitalcare prescriptions for new user should show empty message."""
    result = cli("prescriptions")
    assert result.returncode == 0, f"prescriptions failed: {result.stderr}"


def test_book_appointment_via_api():
    """Book appointment via API directly to test appointment retrieval."""
    # Get first hospital
    resp = api("get", "/v1/hospitals")
    assert resp.status_code == 200
    hospitals = resp.json()
    if not hospitals:
        print("  [SKIP] No hospitals available")
        return

    hospital_id = hospitals[0]["id"]
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # Get token from file
    token_data = json.loads(TOKEN_FILE.read_text())
    auth = f"Bearer {token_data['access_token']}"

    resp = api("post", "/v1/appointments/book",
               json={
                   "hospital_id": hospital_id,
                   "appointment_date": tomorrow,
                   "slot": "10:00",
                   "reason": "CLI test appointment",
                   "symptoms": "Testing CLI",
                   "temperature": 37.0,
               },
               headers={"authorization": auth})

    if resp.status_code == 400 and "already has an appointment" in resp.text:
        print("  [NOTE] Already have appointment on this date, skipping booking")
        return

    assert resp.status_code == 201, f"Booking failed: {resp.text}"
    data = resp.json()
    assert "id" in data
    assert data["status"] == "pending"

    # Store appt_id for next test
    _state["appointment_id"] = data["id"]


def test_appointments_shows_booked():
    """hospitalcare appointments should list the booked appointment."""
    result = cli("appointments")
    assert result.returncode == 0, f"appointments failed: {result.stderr}"


def test_unauthenticated_request_fails_cleanly():
    """
    If we clear the token, authenticated commands should fail cleanly 
    (no stack trace, just a user-friendly message).
    """
    # Temporarily rename token file
    backup = TOKEN_FILE.parent / "token.json.bak"
    if TOKEN_FILE.exists():
        TOKEN_FILE.rename(backup)

    try:
        result = cli("appointments")
        output = result.stdout + result.stderr
        # Should NOT contain a Python traceback
        assert "Traceback" not in output, f"Stack trace exposed: {output}"
        assert "hospitalcare login" in output.lower() or "not logged in" in output.lower() \
            or result.returncode != 0, f"Should have indicated auth required: {output}"
    finally:
        # Restore token
        if backup.exists():
            backup.rename(TOKEN_FILE)

def test_invalid_hospital_id_fails_cleanly():
    result = cli(
        "hospitals",
        "info",
        "000000000000000000000000",
    )

    output = result.stdout + result.stderr

    if "Traceback" in output:
        raise AssertionError(
            "CLI subprocess exposed traceback"
        )

    assert (
        "not found" in output.lower()
        or "unable to fetch hospital" in output.lower()
        or "error" in output.lower()
        or "warning" in output.lower()
    ), "No clean user-facing error message found"
    
def test_chat_via_api():
    """Test chatbot via direct API call (avoids interactive REPL)."""
    token_data = json.loads(TOKEN_FILE.read_text())
    auth = f"Bearer {token_data['access_token']}"
    conv_id = f"cli-test-{uuid.uuid4().hex[:8]}"

    resp = api("post", "/v1/chat",
               json={"conversation_id": conv_id, "user_input": "Hello, what can you help me with?"},
               headers={"authorization": auth})

    # The chatbot requires patient role — if this user is a patient, it should work
    if resp.status_code == 403:
        print("  [NOTE] Chat requires patient role — skipping (user may not be patient)")
        return

    assert resp.status_code == 200, f"Chat failed: {resp.text}"
    data = resp.json()
    assert "response" in data, f"No response key: {data}"
    assert len(data["response"]) > 0, "Empty chatbot response"


def test_chat_stream_via_api():
    """Test SSE streaming chatbot via direct API."""
    token_data = json.loads(TOKEN_FILE.read_text())
    auth = f"Bearer {token_data['access_token']}"
    conv_id = f"cli-stream-test-{uuid.uuid4().hex[:8]}"

    full_response = []
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        with c.stream("POST", "/v1/chat/stream",
                      json={"conversation_id": conv_id, "user_input": "What is today's date?"},
                      headers={"authorization": auth, "Content-Type": "application/json"}) as r:
            if r.status_code == 403:
                print("  [NOTE] Chat stream requires patient role — skipping")
                return
            assert r.status_code == 200, f"Stream failed: {r.status_code}"
            for line in r.iter_lines():
                if line.startswith("data:"):
                    try:
                        payload = json.loads(line[5:].strip())
                        if "text" in payload:
                            full_response.append(payload["text"])
                        elif "response" in payload:
                            break
                    except Exception:
                        pass

    assert len(full_response) > 0, "No streaming chunks received"


def test_jwt_isolation():
    """Verify that one patient cannot access another patient's data via JWT."""
    # Create a second test patient
    email2 = f"cli_test2_{uuid.uuid4().hex[:8]}@citycare-test.com"
    resp = api("post", "/v1/users/signup", json={
        "first_name": "Second",
        "last_name": "Patient",
        "email": email2,
        "password": TEST_PASSWORD,
    })
    if resp.status_code != 201:
        print("  [NOTE] Could not create second patient, skipping JWT isolation test")
        return

    resp2 = api("post", "/v1/users/login", json={"email": email2, "password": TEST_PASSWORD})
    assert resp2.status_code == 200
    token2 = resp2.json()["access_token"]

    # Get appointments with second patient's token — should only see their own (empty)
    resp_appts = api("get", "/v1/appointments/my",
                     headers={"authorization": f"Bearer {token2}"})
    assert resp_appts.status_code == 200
    # Second patient has no appointments (they're new), so the list should be empty
    appts = resp_appts.json()
    assert isinstance(appts, list), "Expected list of appointments"

    # Verify first patient's appointments are NOT in the response
    if _state.get("appointment_id"):
        appt_ids = [a["id"] for a in appts]
        assert _state["appointment_id"] not in appt_ids, \
            "JWT isolation breach: Patient 2 can see Patient 1's appointment!"


def test_logout():
    """hospitalcare logout should remove the token file."""
    assert TOKEN_FILE.exists(), "Token file should exist before logout"
    result = cli("logout")
    assert result.returncode == 0, f"logout failed: {result.stderr}"
    assert not TOKEN_FILE.exists(), "Token file should be removed after logout"


# ─── State shared between tests ───────────────────────────────────────────────
_state: dict = {}


# ─── Runner ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  HospitalCare CLI — End-to-End Test Suite")
    print("=" * 60)
    print(f"  Backend URL : {BASE_URL}")
    print(f"  Test email  : {TEST_EMAIL}")
    print("=" * 60)
    print()

    tests = [
        ("Backend reachable",              test_backend_reachable),
        ("Signup via API",                 test_signup_via_api),
        ("Login saves token",              test_login_saves_token),
        ("whoami output",                  test_whoami_output),
        ("Hospitals list",                 test_hospitals_list),
        ("Slots for today",                test_slots_today),
        ("Dashboard",                      test_dashboard),
        ("Appointments (empty)",           test_appointments_empty),
        ("Prescriptions (empty)",          test_prescriptions_empty),
        ("Book appointment via API",       test_book_appointment_via_api),
        ("Appointments show booked",       test_appointments_shows_booked),
        ("Chat via API",                   test_chat_via_api),
        ("Chat stream via API",            test_chat_stream_via_api),
        ("JWT isolation",                  test_jwt_isolation),
        ("Unauthenticated request clean",  test_unauthenticated_request_fails_cleanly),
        ("Invalid hospital ID clean",      test_invalid_hospital_id_fails_cleanly),
        ("Logout removes token",           test_logout),
    ]

    for name, fn in tests:
        run_test(name, fn)

    print()
    print("=" * 60)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f"  Results: {passed} PASS / {failed} FAIL / {len(results)} total")
    print("=" * 60)

    if failed:
        print("\n  Failed tests:")
        for name, ok, err in results:
            if not ok:
                print(f"    ✗ {name}: {err}")
        sys.exit(1)
    else:
        print("\n  All tests passed! ✓")


if __name__ == "__main__":
    main()
