# Chatbot Module Migration Guide

This guide explains how to migrate the modular chatbot folder to another project.

## Overview

The chatbot folder contains a self-contained, reusable chatbot system built with:
- **Gemini 3.5 Flash Lite** for conversational AI
- **RAG Service** for prescription knowledge retrieval using vector embeddings
- **Ollama** for local embeddings
- **FastAPI** for API endpoints
- **JWT** for authentication

## Pre-Migration Checklist

- [ ] Target project has Python 3.10+ installed
- [ ] MongoDB is set up and accessible
- [ ] Ollama is running with `nomic-embed-text` model
- [ ] Google Gemini API key obtained
- [ ] FastAPI and required dependencies available

## Step 1: Copy Chatbot Folder

Copy the entire `chatbot` folder to your target project's root directory:

```bash
cp -r chatbot /path/to/target-project/
```

## Step 2: Install Dependencies

Add these to your `requirements.txt`:

```txt
google-genai>=0.4.0
httpx>=0.24.0
python-jose[cryptography]>=3.3.0
python-dotenv>=1.0.0
pydantic>=2.0.0
fastapi>=0.100.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

Create or update `.env` file in your project root with:

```env
# From chatbot/config/.env.example - update with your values
API_KEY=your_actual_gemini_api_key
secret=your_secret_key_change_me
algorithm=HS256
OLLAMA_URL=http://localhost:11434/api/embed
MONGODB_URL=mongodb://localhost:27017
MONGODB_NAME=your_database_name
```

## Step 4: Update Imports

In your main FastAPI app file (e.g., `main.py` or `app.py`):

### Option A: Using Factory Function (Recommended)

```python
from fastapi import FastAPI
from chatbot.api.routes import create_chatbot_router
from your_project.controllers.appointment_controller import AppointmentController

app = FastAPI()

# Create appointment controller with your domain logic
appointment_controller = AppointmentController()

# Create chatbot router with dependencies
chatbot_router = create_chatbot_router(appointment_controller=appointment_controller)

# Include chatbot routes
app.include_router(chatbot_router, tags=["Chatbot"])
```

### Option B: Manual Integration

```python
from fastapi import FastAPI
from chatbot.core.controller import ChatbotController
from your_project.controllers.appointment_controller import AppointmentController

app = FastAPI()

# Initialize controllers
appointment_controller = AppointmentController()
chatbot_controller = ChatbotController(appointment_controller)

# Manually define routes
@app.post("/v1/chat")
async def chat(conversation_id: str, user_input: str, authorization: str):
    reply = await chatbot_controller.run_turn(
        conversation_id, user_input, authorization
    )
    return {"response": reply}
```

## Step 5: Adapt Database Models

If your project uses different ORM/models:

1. **For RAG Service**: Update import in `chatbot/core/rag_service.py`:

```python
# Change this line:
# from core.database.database import MongoDatabase

# To your database import:
from your_project.database import get_mongo_db
```

2. **For Prescription Model**: The chatbot expects prescriptions with:
   - `id`, `appointment_id`, `patient_id`, `doctor_id`
   - `diagnosis`, `medicines`, `notes`, `created_at`

Update if your model structure differs.

## Step 6: Adapt Authentication

If your authentication differs from the original:

1. Update `chatbot/common/auth_helpers.py`:

```python
# Modify verify_token() to match your JWT implementation
def verify_token(token: str) -> dict:
    # Your custom token verification logic
    pass
```

2. Update secret key loading:

```python
# Ensure SECRET_KEY and ALGORITHM match your setup
SECRET_KEY = os.environ.get("secret", "your-key")
ALGORITHM = os.environ.get("algorithm", "HS256")
```

## Step 7: Adapt Appointment Controller

The chatbot depends on an AppointmentController with these methods:

```python
class AppointmentController:
    async def get_schedule(self, appointment_date: date, hospital_id: str = None) -> dict:
        """Return available slots for given date."""
        
    async def book_appointment(self, request_data: dict, authorization: str) -> dict:
        """Book an appointment for the authenticated patient."""
        
    async def get_my_appointments(self, authorization: str) -> list[dict]:
        """Get appointments for authenticated patient."""
```

If your controller has different method signatures, either:
- Adapt your controller to match these signatures
- Modify `chatbot/core/controller.py` to call your methods differently

## Step 8: Test Configuration

Create a test script `test_chatbot.py`:

```python
import asyncio
from chatbot.common.embedding_service import get_embedding
from chatbot.common.logger import logger

async def test_ollama():
    """Test Ollama connection."""
    try:
        embedding = await get_embedding("test")
        print(f"✓ Ollama working. Embedding dimension: {len(embedding)}")
    except Exception as e:
        print(f"✗ Ollama error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama())
```

Run: `python test_chatbot.py`

## Step 9: Update API Documentation

The chatbot provides these endpoints:

- `POST /v1/chat` - Send message and get response
- `POST /v1/chat/stream` - Streaming response with SSE
- `GET /chat-history` - Get conversation history

Add to your API docs:

```python
app.include_router(
    chatbot_router,
    prefix="/api/chatbot",
    tags=["Chatbot"]
)
```

## Step 10: Deploy

Ensure production environment has:

```bash
# Required services running
- MongoDB instance
- Ollama service with nomic-embed-text model
- Google Gemini API access
- All environment variables set
```

## Customization Guide

### Changing the System Prompt

Edit `chatbot/core/controller.py`:

```python
SYSTEM_INSTRUCTION = """
Your custom system prompt here.
This defines how the chatbot behaves.
"""
```

### Adding New Tools

In `chatbot/core/controller.py`, add to `TOOL_DECLARATIONS`:

```python
genai_types.FunctionDeclaration(
    name="your_tool",
    description="What it does",
    parameters=genai_types.Schema(...)
)
```

Then handle in `_execute_tool()`:

```python
elif tool_name == "your_tool":
    result = await self.your_method(args)
    return result
```

### Customizing RAG

In `chatbot/core/rag_service.py`:

```python
# Change similarity threshold
similarity_threshold=0.5  # Instead of 0.4

# Change number of results
top_k=5  # Instead of 3
```

## Troubleshooting

### "API_KEY not found"
- Check `.env` file exists in project root
- Verify `API_KEY=` is set correctly
- Restart your application

### "Ollama API returned status 404"
- Ensure Ollama is running: `ollama serve`
- Pull model: `ollama pull nomic-embed-text`
- Check OLLAMA_URL in `.env`

### "Database connection not initialized"
- Check MongoDB is running
- Verify MONGODB_URL in `.env`
- Ensure `MongoDatabase` import path is correct

### "No prescription records found"
- Verify patient has prescriptions in database
- Check patient_id is correctly retrieved from JWT
- Ensure prescriptions have been indexed for RAG

## Migration Checklist

- [ ] Chatbot folder copied to target project
- [ ] Dependencies installed
- [ ] `.env` configured with API keys
- [ ] FastAPI app imports chatbot router
- [ ] AppointmentController adapted/integrated
- [ ] Authentication verified
- [ ] Database models compatible
- [ ] Test endpoints working
- [ ] System prompt customized (if needed)
- [ ] Documentation updated

## Support

For issues, check:
1. Environment variables are set
2. External services (Ollama, MongoDB, Gemini) are accessible
3. Import paths match your project structure
4. Authentication tokens are valid

## Version History

- **v1.0.0** (2024-08-14) - Initial modular release
