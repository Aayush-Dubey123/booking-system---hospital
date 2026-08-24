# Chatbot Module Structure

## Directory Layout

```
chatbot/
├── __init__.py                 # Module initialization & exports
├── README.md                   # Main documentation
├── STRUCTURE.md               # This file - directory layout
├── requirements.txt           # Python dependencies
│
├── core/                      # Core chatbot logic
│   ├── __init__.py            # Core module exports
│   ├── controller.py          # Gemini controller & tool execution
│   └── rag_service.py         # Vector search for prescriptions
│
├── api/                       # API endpoints
│   ├── __init__.py            # API module exports
│   └── routes.py              # FastAPI routes & factory function
│
├── common/                    # Shared utilities
│   ├── __init__.py            # Common utilities exports
│   ├── logger.py              # Logging utility
│   ├── embedding_service.py   # Ollama integration for embeddings
│   └── auth_helpers.py        # JWT authentication & token utilities
│
├── config/                    # Configuration & settings
│   ├── __init__.py            # Config module exports
│   ├── settings.py            # Configuration management class
│   └── .env.example           # Environment variables template
│
└── docs/                      # Documentation & examples
    ├── QUICKSTART.md          # Quick start guide
    ├── MIGRATION_GUIDE.md     # Detailed migration instructions
    ├── INTEGRATION_EXAMPLE.py # Code examples for integration
    └── API.md                 # Complete API documentation
```

## File Descriptions

### Core Module (`core/`)

#### `controller.py`
Main chatbot controller integrating Google Gemini API.

**Key Classes:**
- `ChatbotController`: Main class handling conversations and tool calls

**Key Methods:**
- `run_turn()`: Process a single conversation turn
- `get_history()`: Retrieve conversation history
- `_execute_tool()`: Execute tool calls

**Key Components:**
- `SYSTEM_INSTRUCTION`: Defines chatbot behavior
- `TOOL_DECLARATIONS`: Available tools (slots, booking, appointments, prescriptions)
- `conversations`: In-memory conversation storage

#### `rag_service.py`
RAG (Retrieval-Augmented Generation) service for prescription retrieval.

**Key Classes:**
- `RAGService`: Vector search for prescriptions using MongoDB

**Key Methods:**
- `index_prescription()`: Store prescription embedding in vector DB
- `search_prescriptions()`: Search for prescriptions using vector similarity

**Features:**
- Cosine similarity calculation
- MongoDB Atlas vector search (with fallback)
- Patient data isolation

### API Module (`api/`)

#### `routes.py`
FastAPI routes and router factory.

**Key Functions:**
- `create_chatbot_router()`: Factory function to create configured router

**Endpoints:**
- `POST /v1/chat`: Non-streaming chat
- `POST /v1/chat/stream`: Streaming chat with SSE
- `GET /chat-history`: Retrieve conversation history

### Common Utilities (`common/`)

#### `logger.py`
Logging utility for consistent log formatting.

**Functions:**
- `logger(name)`: Create configured logger instance

#### `embedding_service.py`
Integration with Ollama for generating text embeddings.

**Functions:**
- `get_embedding(text)`: Generate vector embedding using Ollama

**Features:**
- Async HTTP client with timeout
- Fallback between API versions
- Dynamic dimension handling

#### `auth_helpers.py`
JWT authentication and token management.

**Functions:**
- `verify_token(token)`: Verify and decode JWT
- `require_role(payload, role)`: Check user role
- `create_token(data, expires_delta)`: Create new JWT token

### Configuration Module (`config/`)

#### `settings.py`
Configuration management with environment variable loading.

**Key Classes:**
- `ChatbotConfig`: Configuration class with defaults

**Configuration Areas:**
- API & Authentication
- Gemini Model settings
- RAG parameters
- Ollama settings
- Database configuration
- Feature flags

#### `.env.example`
Template for environment variables needed by chatbot.

### Documentation (`docs/`)

#### `QUICKSTART.md`
5-minute setup guide for getting started.

#### `MIGRATION_GUIDE.md`
Comprehensive step-by-step migration to new projects.

**Includes:**
- Pre-migration checklist
- Installation steps
- Configuration guide
- Database adaptation
- Authentication adaptation
- Testing procedures
- Customization guide
- Troubleshooting

#### `INTEGRATION_EXAMPLE.py`
Multiple code examples showing different integration patterns.

**Examples:**
1. Basic integration with factory function
2. FastAPI application setup
3. Custom integration with direct instantiation
4. Custom routes
5. Different authentication schemes
6. RAG service separation
7. Full application setup
8. Testing patterns

#### `API.md`
Complete API endpoint documentation.

**Includes:**
- Authentication details
- Endpoint specifications with examples
- Tool descriptions
- Sample conversations
- Error handling
- Rate limiting
- Security considerations

## Usage Flow

### Setup Flow
```
1. Copy chatbot/ to target project
   ↓
2. Install dependencies from requirements.txt
   ↓
3. Configure .env variables
   ↓
4. Import create_chatbot_router() from chatbot.api.routes
   ↓
5. Create router with AppointmentController dependency
   ↓
6. Include router in FastAPI app
   ↓
7. Test endpoints
```

### Runtime Flow
```
User Message
    ↓
POST /v1/chat or /v1/chat/stream
    ↓
ChatbotController.run_turn()
    ↓
Gemini API (with tools)
    ├─→ get_available_slots → AppointmentController
    ├─→ book_appointment → AppointmentController
    ├─→ my_appointments → AppointmentController
    └─→ get_prescription_info → RAGService → MongoDB
    ↓
Gemini Response
    ↓
Return to Client (streaming or non-streaming)
```

### Vector Search Flow (RAG)
```
Prescription Created
    ↓
Create text chunk from prescription data
    ↓
Generate embedding via Ollama
    ↓
Store in MongoDB prescription_vectors collection
    ↓
---Later---
    ↓
Patient asks about prescription
    ↓
Chatbot calls get_prescription_info tool
    ↓
RAGService generates query embedding
    ↓
Vector search in MongoDB (patient-scoped)
    ↓
Return top-k similar prescriptions
    ↓
Gemini includes results in context
    ↓
Chatbot answers based on prescriptions
```

## Configuration Hierarchy

```
Default Values (in settings.py)
    ↓
Environment Variables (.env)
    ↓
Runtime Configuration (in application)
```

## Dependency Injection

The module uses constructor-based dependency injection:

```python
# Create router with external dependency
appointment_controller = YourAppointmentController()
chatbot_router = create_chatbot_router(
    appointment_controller=appointment_controller
)

# Or manual injection
chatbot_controller = ChatbotController(appointment_controller)
```

## External Dependencies

**Required Services:**
- Google Gemini API (cloud service)
- MongoDB (database)
- Ollama (local embedding service)

**Python Packages:**
- google-genai: Gemini API client
- httpx: HTTP client for Ollama
- python-jose: JWT handling
- fastapi: Web framework
- pydantic: Data validation
- python-dotenv: Environment variable management

## Extension Points

### 1. Custom System Prompt
Edit `SYSTEM_INSTRUCTION` in `controller.py`

### 2. Add New Tools
1. Add to `TOOL_DECLARATIONS` in `controller.py`
2. Handle in `_execute_tool()` method

### 3. Custom Authentication
Override `verify_token()` in `auth_helpers.py` or extend `ChatbotController`

### 4. Database Adaptation
Modify `RAGService` initialization for your database client

### 5. Custom Routes
Use `create_chatbot_router()` return value or extend `routes.py`

## Testing

Recommended test structure:

```python
# tests/test_chatbot.py
import asyncio
from chatbot.common.embedding_service import get_embedding
from chatbot.core.rag_service import RAGService

async def test_ollama():
    """Test Ollama connection"""
    embedding = await get_embedding("test")
    assert len(embedding) > 0

async def test_rag_service():
    """Test RAG service initialization"""
    rag = RAGService()
    assert rag.collection is not None
```

## Performance Considerations

- **Conversation storage**: In-memory (consider persistent store for production)
- **RAG queries**: MongoDB vector search (or fallback to similarity)
- **Embeddings**: Cached by Ollama, < 500ms per call
- **Gemini API**: 1-3 seconds per request
- **Streaming**: First token < 500ms, subsequent < 100ms

## Security Considerations

- ✅ JWT-based authentication required for all endpoints
- ✅ Role-based access control (patient-only)
- ✅ Patient data isolation in RAG queries
- ✅ No credential storage in code (uses .env)
- ✅ Input validation via Pydantic

## Version Information

- **Chatbot Module Version**: 1.0.0
- **Python**: 3.10+
- **FastAPI**: 0.100.0+
- **Pydantic**: 2.0.0+
- **Google Genai**: 0.4.0+

---

**Last Updated**: 2024-08-14
