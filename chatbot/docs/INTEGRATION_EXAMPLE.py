"""
Example of integrating the chatbot module into a FastAPI project.

This shows how to use the chatbot in a new project with different database/auth setup.
"""

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
import asyncio

# Your existing imports
from your_project.database import get_db
from your_project.models import User, Appointment
from your_project.auth import verify_jwt_token

# Chatbot imports
from chatbot.api.routes import create_chatbot_router
from chatbot.core.controller import ChatbotController
from chatbot.common.logger import logger

logging = logger(__name__)


# ============================================================================
# EXAMPLE 1: Basic Integration with Factory Function (Recommended)
# ============================================================================

class YourAppointmentController:
    """Your project's appointment controller with chatbot compatibility."""

    def __init__(self, db):
        self.db = db

    async def get_schedule(self, appointment_date, hospital_id=None):
        """Get available slots for a given date."""
        # Your database query
        slots = await self.db.appointments.find({
            "date": appointment_date,
            "status": "available",
            **({"hospital_id": hospital_id} if hospital_id else {})
        }).to_list(None)

        return {
            "appointment_date": str(appointment_date),
            "slots": [s["time_slot"] for s in slots],
            "hospital_id": hospital_id
        }

    async def book_appointment(self, request_data, authorization):
        """Book an appointment for the patient."""
        # Extract user from token
        payload = verify_jwt_token(authorization)
        patient_id = payload["user_id"]

        # Create appointment
        appointment = {
            "patient_id": patient_id,
            "hospital_id": request_data["hospital_id"],
            "date": request_data["appointment_date"],
            "slot": request_data["slot"],
            "reason": request_data["reason"],
            "symptoms": request_data["symptoms"],
            "temperature": request_data["temperature"],
            "status": "pending"
        }

        result = await self.db.appointments.insert_one(appointment)
        appointment["_id"] = result.inserted_id
        return appointment

    async def get_my_appointments(self, authorization):
        """Get all appointments for the authenticated patient."""
        payload = verify_jwt_token(authorization)
        patient_id = payload["user_id"]

        appointments = await self.db.appointments.find({
            "patient_id": patient_id
        }).to_list(None)

        return appointments


# ============================================================================
# EXAMPLE 2: Setting up FastAPI Application
# ============================================================================

def create_app():
    """Create and configure FastAPI application with chatbot."""

    app = FastAPI(
        title="My Healthcare API",
        version="1.0.0",
        description="API with integrated chatbot"
    )

    # Initialize your database
    # db = get_db()  # Your database initialization

    # Create appointment controller (your adapter)
    # appointment_controller = YourAppointmentController(db)

    # Create chatbot router using factory function
    # chatbot_router = create_chatbot_router(
    #     appointment_controller=appointment_controller
    # )

    # Include chatbot routes
    # app.include_router(chatbot_router, prefix="/api/chatbot", tags=["Chatbot"])

    return app


# ============================================================================
# EXAMPLE 3: Custom Integration with Direct Controller Instantiation
# ============================================================================

class CustomChatbotSetup:
    """Custom setup if you need more control."""

    def __init__(self, db):
        self.db = db
        self.appointment_controller = YourAppointmentController(db)
        self.chatbot_controller = ChatbotController(self.appointment_controller)

    async def handle_chat(self, conversation_id: str, user_input: str, token: str):
        """Handle a chat message."""
        try:
            response = await self.chatbot_controller.run_turn(
                conversation_id, user_input, token
            )
            return {"status": "success", "response": response}
        except Exception as e:
            logging.error(f"Chat error: {e}")
            return {"status": "error", "error": str(e)}


# ============================================================================
# EXAMPLE 4: Custom Routes if Needed
# ============================================================================

async def setup_custom_routes(app: FastAPI, chatbot_setup: CustomChatbotSetup):
    """Setup custom chatbot routes with additional logic."""

    class ChatMessage(BaseModel):
        conversation_id: str
        message: str

    @app.post("/api/chat")
    async def chat_endpoint(
        request: ChatMessage,
        authorization: str = Header(...)
    ):
        """Custom chat endpoint with logging and rate limiting."""
        logging.info(f"Chat: {request.conversation_id} - {len(request.message)} chars")

        result = await chatbot_setup.handle_chat(
            request.conversation_id,
            request.message,
            authorization
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        return {
            "conversation_id": request.conversation_id,
            "response": result["response"]
        }


# ============================================================================
# EXAMPLE 5: Adapting to Different Authentication Schemes
# ============================================================================

class CustomAuthChatbot(ChatbotController):
    """Extend ChatbotController if your auth is different."""

    async def run_turn(self, conversation_id: str, user_text: str, authorization: str) -> str:
        """Override if you have custom auth logic."""
        # Your custom token verification
        # payload = your_custom_verify_token(authorization)

        # Call parent implementation
        return await super().run_turn(conversation_id, user_text, authorization)


# ============================================================================
# EXAMPLE 6: Integrating RAG Service Separately
# ============================================================================

from chatbot.core.rag_service import RAGService

class EnhancedAppointmentController(YourAppointmentController):
    """Appointment controller with RAG integration example."""

    async def get_prescription_info(self, patient_id: str, query: str):
        """Get prescription information using RAG."""
        rag_service = RAGService()

        try:
            results = await rag_service.search_prescriptions(
                patient_id=patient_id,
                query=query,
                top_k=3,
                similarity_threshold=0.4
            )

            if not results:
                return {"prescriptions": None}

            return {
                "prescriptions": [
                    {
                        "text": r["text"],
                        "relevance_score": r["score"]
                    }
                    for r in results
                ]
            }
        except Exception as e:
            logging.error(f"RAG error: {e}")
            return {"error": str(e)}


# ============================================================================
# EXAMPLE 7: Full Application Setup
# ============================================================================

def setup_full_app():
    """Complete setup example."""

    app = FastAPI(
        title="Hospital Management API",
        version="2.0.0"
    )

    # Your database initialization
    # db = get_db()

    # Setup appointment controller
    # appointment_controller = EnhancedAppointmentController(db)

    # Create chatbot router
    # chatbot_router = create_chatbot_router(
    #     appointment_controller=appointment_controller
    # )

    # Include routes
    # app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])

    # Additional routes
    # @app.get("/health")
    # async def health_check():
    #     return {"status": "healthy"}

    return app


# ============================================================================
# EXAMPLE 8: Testing the Chatbot
# ============================================================================

async def test_chatbot_integration():
    """Test chatbot integration."""

    # Mock components
    class MockDB:
        async def find(self, query):
            return [{"time_slot": "10:00"}, {"time_slot": "14:00"}]

        async def insert_one(self, doc):
            class Result:
                inserted_id = "mock_id"
            return Result()

    # Create controller
    db = MockDB()
    controller = YourAppointmentController(db)

    # Get schedule
    schedule = await controller.get_schedule(None, "hospital123")
    print(f"Available slots: {schedule['slots']}")

    # Book appointment (this would need a valid JWT in real usage)
    # appointment = await controller.book_appointment(
    #     {
    #         "hospital_id": "hospital123",
    #         "appointment_date": "2024-08-20",
    #         "slot": "10:00",
    #         "reason": "Checkup",
    #         "symptoms": "None",
    #         "temperature": 37.0
    #     },
    #     "fake-jwt-token"
    # )


if __name__ == "__main__":
    # Uncomment to run tests
    # asyncio.run(test_chatbot_integration())

    # Create and run app
    app = setup_full_app()

    # Run with: uvicorn integration_example:app --reload
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
