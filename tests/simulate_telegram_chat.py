import asyncio
import os
import sys
from pathlib import Path

# Ensure citycare-backend is in python path
backend_path = Path(__file__).resolve().parent.parent / "citycare-backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# pyrefly: ignore [missing-import]
from core.controllers.chatbot_controller import ChatbotController
# pyrefly: ignore [missing-import]
from core.database.database import connect_to_mongo, close_mongo_connection

async def simulate_chat():
    print("Connecting to Mongo...")
    await connect_to_mongo()
    
    controller = ChatbotController()
    chat_id = "test_telegram_sim_9999"
    
    print("\n==================================================")
    print("   TELEGRAM CONVERSATION SIMULATION START         ")
    print("==================================================")
    
    # We define a helper to print message and reply
    async def send_msg(prompt_text: str):
        print(f"\n👤 Patient: {prompt_text}")
        reply = await controller.run_telegram_turn(chat_id, prompt_text)
        print(f"🤖 Bot: {reply}")
        await asyncio.sleep(6)  # Avoid hitting Gemini API rate limits (429 Resource Exhausted)
        return reply


    # Step 1: Greeting
    await send_msg("Hello!")

    # Step 2: Signup a new user john.doe@example.com
    # Note: If john already exists, it might return an error, but let's test if the tool is invoked.
    await send_msg("Please register a new account for me. My name is John Doe, email is john.doe@example.com and password is Pass1234!")

    # Step 3: Login
    await send_msg("Can you log me in with my email john.doe@example.com and password Pass1234!?")

    # Step 4: List hospitals
    await send_msg("Show me the available hospitals.")

    # Step 5: Discover doctors at a specific hospital
    # We'll use the ID of the hospital seeded or returned by list_hospitals.
    # To be general, we ask "Who are the doctors at CityCare NGP Clinic?" and let the AI find it.
    await send_msg("Who are the doctors at CityCare NGP Clinic?")

    # Step 6: Check availability / schedule
    await send_msg("Check open slots for 2026-09-01.")

    # Step 7: Booking attempt (should ask for missing details or confirm if details are complete)
    # We need to provide hospital_id, doctor_id, appointment_date, slot.
    # In the seed data:
    # "CityCare NGP Clinic" exists. Let's ask to book an appointment with Dr. One.
    await send_msg("I want to book an appointment with Dr. One at CityCare NGP Clinic on 2026-09-01 at 10:00 for a regular wellness checkup.")

    # Step 8: Confirm booking (this should trigger the book_appointment tool)
    await send_msg("Yes, please confirm and book it.")

    # Step 9: View appointments
    await send_msg("Show my booked appointments.")

    # Step 10: View prescriptions
    await send_msg("Do I have any prescriptions?")

    # Step 11: Cancel appointment (should ask for confirmation first, but not invoke any tool)
    await send_msg("I need to cancel my appointment.")

    # Step 12: Confirm cancellation (should explain the limitation and direct to support)
    await send_msg("Yes, I'm sure I want to cancel it.")

    print("\n==================================================")
    print("   TELEGRAM CONVERSATION SIMULATION END           ")
    print("==================================================")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(simulate_chat())
