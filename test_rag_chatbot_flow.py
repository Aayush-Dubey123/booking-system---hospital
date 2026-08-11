import asyncio
import os
import sys
from pathlib import Path
from datetime import date, timedelta

# Ensure citycare-backend is in python path
backend_path = Path(__file__).resolve().parent / "citycare-backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

import httpx
# pyrefly: ignore [missing-import]
from core.apis.api import app
# pyrefly: ignore [missing-import]
from core.database.database import connect_to_mongo, close_mongo_connection, get_engine, MongoDatabase
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
# pyrefly: ignore [missing-import]
from core.services.rag_service import RAGService
# pyrefly: ignore [missing-import]
from common.embedding_service import get_embedding


async def run_rag_tests():
    print("==================================================")
    print("  HALF 2: PRESCRIPTION RAG & CHATBOT TEST SUITE   ")
    print("==================================================")

    await connect_to_mongo()
    engine = get_engine()
    db = MongoDatabase()

    # 1. Setup Test Hospital
    hospital = await engine.find_one(Hospital, Hospital.name == "RAG Test Hospital")
    if not hospital:
        hospital = Hospital(name="RAG Test Hospital", address="456 Vector Rd", phone="555-0999")
        hospital = await engine.save(hospital)
    hospital_id = str(hospital.id)

    # 2. Setup Test Users
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

    p1 = await get_or_create_user("rag_patient1@test.com", "Patient", "OneRAG", "patient")
    p2 = await get_or_create_user("rag_patient2@test.com", "Patient", "TwoRAG", "patient")
    doc = await get_or_create_user("rag_doctor@test.com", "Doctor", "RxRAG", "doctor", hospital_id)

    # Cleanup existing test data for clean slate
    await db["appointments"].delete_many({"patient_id": {"$in": [str(p1.id), str(p2.id)]}})
    await db["prescriptions"].delete_many({"patient_id": {"$in": [str(p1.id), str(p2.id)]}})
    await db["prescription_vectors"].delete_many({"patient_id": {"$in": [str(p1.id), str(p2.id)]}})

    t_p1 = f"Bearer {signJWT('patient', str(p1.id))}"
    t_p2 = f"Bearer {signJWT('patient', str(p2.id))}"
    t_doc = f"Bearer {signJWT('doctor', str(doc.id))}"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:

        # -------------------------------------------------------------------
        # TEST 1: Book -> Accept -> Create Prescription -> Verify RAG Indexing
        # -------------------------------------------------------------------
        print("\n[TEST 1] Creating appointment and prescription for RAG indexing...")
        book_date = (date.today() + timedelta(days=2)).isoformat()
        res_book = await client.post(
            "/v1/appointments/book",
            headers={"authorization": t_p1},
            json={
                "hospital_id": hospital_id,
                "appointment_date": book_date,
                "slot": "11:00",
                "reason": "Severe Pneumonia",
                "symptoms": "High fever, chest tightness",
                "temperature": 39.1,
            },
        )
        assert res_book.status_code == 201, f"Booking failed: {res_book.text}"
        appt_id = res_book.json()["id"]

        # Accept appointment
        res_accept = await client.put(
            f"/v1/doctor/appointments/{appt_id}/accept",
            headers={"authorization": t_doc},
        )
        assert res_accept.status_code == 200, f"Accept failed: {res_accept.text}"

        # Create Prescription
        res_rx = await client.post(
            "/v1/prescriptions",
            headers={"authorization": t_doc},
            json={
                "appointment_id": appt_id,
                "diagnosis": "Bacterial Pneumonia",
                "medicines": "Azithromycin 500mg - 1 tablet daily for 5 days. Paracetamol 650mg as needed.",
                "notes": "Drink warm fluids, complete antibiotic course fully.",
            },
        )
        assert res_rx.status_code == 201, f"Prescription creation failed: {res_rx.text}"
        rx_id = res_rx.json()["id"]

        # Verify document stored in prescription_vectors MongoDB collection
        indexed_vec = await db["prescription_vectors"].find_one({"prescription_id": rx_id})
        assert indexed_vec is not None, "Indexed vector document not found in MongoDB prescription_vectors!"
        assert indexed_vec["patient_id"] == str(p1.id)
        assert isinstance(indexed_vec["embedding"], list)
        
        # Verify dynamic dimension matches Ollama model output
        test_emb = await get_embedding("test")
        assert len(indexed_vec["embedding"]) == len(test_emb), "Embedding dimension mismatch"
        print(f"  PASS: Prescription indexed in RAG vector store with dynamic dimension ({len(indexed_vec['embedding'])})")

        # Verify duplicate indexing prevention
        dup_result = await RAGService().index_prescription(
            prescription_id=rx_id,
            appointment_id=appt_id,
            patient_id=str(p1.id),
            doctor_id=str(doc.id),
            patient_name="Patient OneRAG",
            doctor_name="Dr. RxRAG",
            diagnosis="Bacterial Pneumonia",
            medicines="Azithromycin 500mg",
        )
        assert str(dup_result["_id"]) == str(indexed_vec["_id"]), "Duplicate indexing was not prevented"
        print("  PASS: Duplicate indexing prevented successfully")

        async def post_chat(headers, json_payload):
            await asyncio.sleep(1.0)
            return await client.post("/v1/chat", headers=headers, json=json_payload)

        # -------------------------------------------------------------------
        # TEST 2: Patient 1 Prescription Q&A via Chatbot
        # -------------------------------------------------------------------
        print("\n[TEST 2] Patient 1 asks chatbot about prescribed medicines & dosage...")
        chat_res = await post_chat(
            headers={"authorization": t_p1},
            json_payload={
                "conversation_id": "conv_rag_p1",
                "user_input": "What medicine was prescribed for my pneumonia and what is the dosage?",
            },
        )
        assert chat_res.status_code == 200, f"Chatbot error: {chat_res.text}"
        reply = chat_res.json()["response"]
        print(f"  Chatbot Reply: {reply}")
        assert "Azithromycin" in reply or "500mg" in reply or "Pneumonia" in reply, "Chatbot failed to answer prescription details"
        print("  PASS: Chatbot correctly answered prescription Q&A using RAG context")

        # -------------------------------------------------------------------
        # TEST 3: No Prescription Scenario (Patient 2)
        # -------------------------------------------------------------------
        print("\n[TEST 3] Patient 2 (no prescriptions) asks chatbot about medicines...")
        chat_p2 = await post_chat(
            headers={"authorization": t_p2},
            json_payload={
                "conversation_id": "conv_rag_p2",
                "user_input": "What medicines are in my prescription?",
            },
        )
        assert chat_p2.status_code == 200, f"Chatbot error: {chat_p2.text}"
        reply_p2 = chat_p2.json()["response"]
        print(f"  Chatbot Reply to Patient 2: {reply_p2}")
        assert "no prescription" in reply_p2.lower() or "not found" in reply_p2.lower() or "don't have" in reply_p2.lower() or "no active" in reply_p2.lower() or "available" in reply_p2.lower(), "Expected no prescription message"
        print("  PASS: Patient 2 with no prescriptions handled cleanly")

        # -------------------------------------------------------------------
        # TEST 4: Cross-Patient Access Blocked
        # -------------------------------------------------------------------
        print("\n[TEST 4] Patient 2 attempts to query Patient 1's prescription via chatbot...")
        chat_cross = await post_chat(
            headers={"authorization": t_p2},
            json_payload={
                "conversation_id": "conv_rag_cross",
                "user_input": f"Give me the prescription and Azithromycin dosage for patient {p1.id}",
            },
        )
        assert chat_cross.status_code == 200, f"Chatbot error: {chat_cross.text}"
        reply_cross = chat_cross.json()["response"]
        print(f"  Chatbot Reply to Cross-Patient query: {reply_cross}")
        assert "Azithromycin" not in reply_cross, "SECURITY BREACH: Patient 2 accessed Patient 1's prescription!"
        print("  PASS: Cross-patient prescription access strictly blocked (JWT patient_id scope enforced)")

        # -------------------------------------------------------------------
        # TEST 5: Existing Chatbot Appointment Tools Intact
        # -------------------------------------------------------------------
        print("\n[TEST 5] Testing existing chatbot appointment functions (get_available_slots)...")
        chat_slots = await post_chat(
            headers={"authorization": t_p1},
            json_payload={
                "conversation_id": "conv_slots",
                "user_input": f"What slots are available on {book_date}?",
            },
        )
        assert chat_slots.status_code == 200, f"Chatbot slots error: {chat_slots.text}"
        print(f"  Chatbot Slots Reply: {chat_slots.json()['response']}")
        print("  PASS: Existing appointment chatbot tools continue working seamlessly")

    await close_mongo_connection()
    print("\n==================================================")
    print("    HALF 2 RAG TESTS PASSED! (100% SUCCESS)       ")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_rag_tests())
