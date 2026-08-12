import asyncio
import os
import sys
from pathlib import Path
from datetime import date, timedelta

# Ensure citycare-backend is in python path
backend_path = Path(__file__).resolve().parent.parent / "citycare-backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

import httpx
# pyrefly: ignore [missing-import]
from core.apis.api import app
# pyrefly: ignore [missing-import]
from core.database.database import connect_to_mongo, close_mongo_connection, get_engine
# pyrefly: ignore [missing-import]
from core.models.user_model import User
# pyrefly: ignore [missing-import]
from core.models.hospital_model import Hospital
# pyrefly: ignore [missing-import]
from core.models.appointment_model import Appointment
# pyrefly: ignore [missing-import]
from core.models.prescription_model import Prescription
# pyrefly: ignore [missing-import]
from common.auth import encrypt_password, signJWT


async def run_tests():
    print("==================================================")
    print("  HOSPITALCARE PRESCRIPTION (HALF 1) TEST SUITE   ")
    print("==================================================")

    await connect_to_mongo()
    engine = get_engine()

    # 1. Setup Test Hospital
    hospital = await engine.find_one(Hospital, Hospital.name == "Test Central Hospital")
    if not hospital:
        hospital = Hospital(name="Test Central Hospital", address="123 Test St", phone="555-0199")
        hospital = await engine.save(hospital)
    hospital_id = str(hospital.id)

    # 2. Setup Users: Patient 1, Patient 2, Doctor 1, Doctor 2
    async def get_or_create_user(email, first, last, role, hosp_id=None):
        u = await engine.find_one(User, User.email == email)
        if not u:
            u = User(
                first_name=first,
                last_name=last,
                email=email,
                password=encrypt_password("Pass1234!"),
                role=role,
                status="active",
                hospital_id=hosp_id,
            )
            u = await engine.save(u)
        return u

    p1 = await get_or_create_user("patient1_rx@test.com", "Patient", "One", "patient")
    p2 = await get_or_create_user("patient2_rx@test.com", "Patient", "Two", "patient")
    d1 = await get_or_create_user("doctor1_rx@test.com", "Doctor", "Alpha", "doctor", hospital_id)
    d2 = await get_or_create_user("doctor2_rx@test.com", "Doctor", "Beta", "doctor", hospital_id)

    # Clean up any existing appointments for test patients
    # pyrefly: ignore [missing-import]
    from core.database.database import MongoDatabase
    db = MongoDatabase()
    await db["appointments"].delete_many({"patient_id": {"$in": [str(p1.id), str(p2.id)]}})
    await db["prescriptions"].delete_many({"patient_id": {"$in": [str(p1.id), str(p2.id)]}})

    t_p1 = f"Bearer {signJWT('patient', str(p1.id))}"
    t_p2 = f"Bearer {signJWT('patient', str(p2.id))}"
    t_d1 = f"Bearer {signJWT('doctor', str(d1.id))}"
    t_d2 = f"Bearer {signJWT('doctor', str(d2.id))}"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:

        # -------------------------------------------------------------------
        # TEST 1: Patient 1 books an appointment -> status must be 'pending'
        # -------------------------------------------------------------------
        print("\n[TEST 1] Patient 1 books an appointment...")
        book_date = (date.today() + timedelta(days=2)).isoformat()
        res = await client.post(
            "/v1/appointments/book",
            headers={"authorization": t_p1},
            json={
                "hospital_id": hospital_id,
                "appointment_date": book_date,
                "slot": "10:00",
                "reason": "Chest Pain & Cough",
                "symptoms": "High fever",
                "temperature": 38.5,
            },
        )
        assert res.status_code == 201, f"Booking failed: {res.text}"
        appt_data = res.json()
        appt_id = appt_data["id"]
        assert appt_data["status"] == "pending", f"Expected 'pending', got {appt_data['status']}"
        assert appt_data["doctor_id"] is None, "Expected doctor_id to be None"
        print(f"  PASS: Appointment {appt_id} booked with status 'pending'")

        # -------------------------------------------------------------------
        # TEST 2: Doctor 2 attempts to prescribe for a pending appointment -> HTTP 400
        # -------------------------------------------------------------------
        print("\n[TEST 2] Doctor 1 attempts to prescribe for a pending appointment...")
        res = await client.post(
            "/v1/prescriptions",
            headers={"authorization": t_d1},
            json={
                "appointment_id": appt_id,
                "diagnosis": "Bronchitis",
                "medicines": "Amoxicillin 500mg",
            },
        )
        assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
        print("  PASS: Pending appointment cannot be prescribed (HTTP 400)")

        # -------------------------------------------------------------------
        # TEST 3: Doctor 1 accepts the pending appointment -> status 'accepted'
        # -------------------------------------------------------------------
        print("\n[TEST 3] Doctor 1 accepts the appointment...")
        res = await client.put(
            f"/v1/doctor/appointments/{appt_id}/accept",
            headers={"authorization": t_d1},
        )
        assert res.status_code == 200, f"Accept failed: {res.text}"
        accepted_data = res.json()
        assert accepted_data["status"] == "accepted", f"Expected 'accepted', got {accepted_data['status']}"
        assert accepted_data["doctor_id"] == str(d1.id), f"Expected doctor {d1.id}, got {accepted_data['doctor_id']}"
        print(f"  PASS: Appointment accepted by Doctor 1 ({d1.id})")

        # -------------------------------------------------------------------
        # TEST 4: Doctor 2 attempts to accept the already accepted appointment -> HTTP 400
        # -------------------------------------------------------------------
        print("\n[TEST 4] Doctor 2 attempts to accept the already accepted appointment...")
        res = await client.put(
            f"/v1/doctor/appointments/{appt_id}/accept",
            headers={"authorization": t_d2},
        )
        assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
        print("  PASS: Second doctor cannot accept an already accepted appointment (HTTP 400)")

        # -------------------------------------------------------------------
        # TEST 5: Doctor 2 (wrong doctor) attempts to prescribe -> HTTP 403
        # -------------------------------------------------------------------
        print("\n[TEST 5] Doctor 2 (wrong doctor) attempts to prescribe for Doctor 1's appointment...")
        res = await client.post(
            "/v1/prescriptions",
            headers={"authorization": t_d2},
            json={
                "appointment_id": appt_id,
                "diagnosis": "Unassigned Doctor Diagnosis",
                "medicines": "Aspirin 100mg",
            },
        )
        assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
        print("  PASS: Wrong doctor cannot create prescription (HTTP 403)")

        # -------------------------------------------------------------------
        # TEST 6: Doctor 1 creates prescription -> REAL PDF & REAL Cloudinary upload
        # -------------------------------------------------------------------
        print("\n[TEST 6] Doctor 1 creates prescription (REAL PDF + Cloudinary Upload)...")
        res = await client.post(
            "/v1/prescriptions",
            headers={"authorization": t_d1},
            json={
                "appointment_id": appt_id,
                "diagnosis": "Acute Bronchitis & Viral Fever",
                "medicines": "1. Amoxicillin 500mg - 1 tab 3x daily\n2. Paracetamol 650mg - as needed",
                "notes": "Drink plenty of warm water. Complete 5-day course.",
            },
        )
        assert res.status_code == 201, f"Prescription creation failed: {res.text}"
        rx_data = res.json()
        rx_id = rx_data["id"]
        pdf_url = rx_data["pdf_url"]
        assert pdf_url and pdf_url.startswith("http"), f"Invalid PDF URL: {pdf_url}"
        print(f"  PASS: Prescription {rx_id} created successfully!")
        print(f"  Cloudinary PDF URL: {pdf_url}")

        # Verify appointment status preserved
        res_appt = await client.get("/v1/appointments/my", headers={"authorization": t_p1})
        my_appts = res_appt.json()
        matching = next((a for a in my_appts if a["id"] == appt_id), None)
        assert matching is not None, "Appointment not found in patient list"
        assert matching["status"] == "accepted", f"Appointment status should remain 'accepted', got {matching['status']}"
        print("  PASS: Appointment status preserved as 'accepted'")

        # -------------------------------------------------------------------
        # TEST 7: Patient 1 views their prescription
        # -------------------------------------------------------------------
        print("\n[TEST 7] Patient 1 fetches their prescription...")
        res = await client.get(
            f"/v1/prescriptions/appointment/{appt_id}",
            headers={"authorization": t_p1},
        )
        assert res.status_code == 200, f"Patient 1 view failed: {res.text}"
        p1_rx = res.json()
        assert p1_rx["pdf_url"] == pdf_url
        print("  PASS: Patient 1 successfully retrieved their prescription & PDF URL")

        # -------------------------------------------------------------------
        # TEST 8: Patient 2 attempts to access Patient 1's prescription -> HTTP 403
        # -------------------------------------------------------------------
        print("\n[TEST 8] Patient 2 attempts to access Patient 1's prescription...")
        res = await client.get(
            f"/v1/prescriptions/appointment/{appt_id}",
            headers={"authorization": t_p2},
        )
        assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"

        res_by_id = await client.get(
            f"/v1/prescriptions/{rx_id}",
            headers={"authorization": t_p2},
        )
        assert res_by_id.status_code == 403, f"Expected 403 by ID, got {res_by_id.status_code}: {res_by_id.text}"
        print("  PASS: Patient 2 blocked from accessing Patient 1's prescription (HTTP 403)")

    await close_mongo_connection()
    print("\n==================================================")
    print("    ALL TESTS PASSED SUCCESSFULLY! (100% PASS)    ")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
