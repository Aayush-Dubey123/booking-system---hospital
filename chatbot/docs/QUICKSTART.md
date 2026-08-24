# Chatbot Quick Start Guide

## Installation (5 minutes)

### 1. Copy Module
```bash
cp -r chatbot /path/to/target-project/
```

### 2. Install Dependencies
```bash
pip install google-genai httpx python-jose python-dotenv pydantic fastapi
```

### 3. Set Environment Variables
Create `.env` in your project root:
```env
API_KEY=your-gemini-api-key
secret=your-secret-key
algorithm=HS256
OLLAMA_URL=http://localhost:11434/api/embed
MONGODB_URL=mongodb://localhost:27017
MONGODB_NAME=your-db-name
```

### 4. Integrate with FastAPI
In your main app file:

```python
from fastapi import FastAPI
from chatbot.api.routes import create_chatbot_router
from your_project.controllers.appointment_controller import AppointmentController

app = FastAPI()

# Initialize chatbot with your appointment controller
appointment_controller = AppointmentController()
chatbot_router = create_chatbot_router(appointment_controller=appointment_controller)

app.include_router(chatbot_router, tags=["Chatbot"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Usage

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Authorization: your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user123",
    "user_input": "Can you check my appointments?"
  }'
```

### Response
```json
{
  "response": "I found 2 upcoming appointments for you..."
}
```

### Streaming Endpoint
```bash
curl -X POST "http://localhost:8000/v1/chat/stream" \
  -H "Authorization: your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user123",
    "user_input": "Tell me about my prescription"
  }' \
  --header 'Accept: text/event-stream'
```

## What It Can Do

✅ **Book Appointments**: Help users schedule appointments  
✅ **View Appointments**: Show user's upcoming appointments  
✅ **Answer Prescriptions**: Retrieve and discuss prescriptions using RAG  
✅ **Natural Conversation**: Understand context and maintain conversation flow  
✅ **Streaming Responses**: Real-time response streaming with Server-Sent Events  
✅ **Tool Calling**: Execute backend operations safely via Gemini  

## Prerequisites

Before starting, ensure:

- **Python 3.10+** installed
- **MongoDB** running (default: `localhost:27017`)
- **Ollama** running with `nomic-embed-text` model:
  ```bash
  ollama serve
  ollama pull nomic-embed-text
  ```
- **Google Gemini API Key** from https://makersuite.google.com

## Project Structure

```
chatbot/
├── core/                 # Core chatbot logic
│   ├── controller.py     # Main chatbot controller
│   └── rag_service.py    # Prescription retrieval
├── api/                  # API endpoints
│   └── routes.py         # FastAPI routes
├── common/               # Shared utilities
│   ├── logger.py         # Logging
│   ├── embedding_service.py  # Ollama integration
│   └── auth_helpers.py   # Authentication
├── config/               # Configuration
│   └── settings.py       # Settings & .env.example
└── docs/                 # Documentation
    ├── QUICKSTART.md     # This file
    ├── MIGRATION_GUIDE.md # Detailed migration
    └── API.md            # API documentation
```

## Common Tasks

### Customize System Prompt
Edit `chatbot/core/controller.py`, modify `SYSTEM_INSTRUCTION`.

### Add New Tool
1. Add `FunctionDeclaration` to `TOOL_DECLARATIONS`
2. Handle in `ChatbotController._execute_tool()`

### Change Gemini Model
In `chatbot/core/controller.py`:
```python
model="gemini-2.0-flash"  # Change from gemini-3.5-flash-lite
```

### Adjust RAG Sensitivity
In `chatbot/core/controller.py`:
```python
await RAGService().search_prescriptions(
    patient_id=patient_id,
    query=query,
    top_k=5,  # More results
    similarity_threshold=0.3  # Lower = more fuzzy
)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `API_KEY not found` | Check `.env` in project root, restart app |
| `Ollama connection failed` | Run `ollama serve`, check OLLAMA_URL |
| `No prescription found` | Patient has no prescriptions in DB or not indexed |
| `Authentication failed` | Verify JWT token format and SECRET_KEY |

## Next Steps

1. Read [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for detailed setup
2. Check [API.md](./API.md) for endpoint documentation
3. Customize system prompt for your domain
4. Add custom tools as needed
5. Test with your data

## Support

- 📚 See MIGRATION_GUIDE.md for detailed instructions
- 🔧 Check troubleshooting section above
- 💬 Review system prompt in controller.py for behavior
- 📖 Read docstrings in core modules

---

**Ready to chat!** 🚀
