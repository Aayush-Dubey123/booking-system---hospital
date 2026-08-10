import json
from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core.controllers.chatbot_controller import ChatbotController
from common.logger import logger

logging = logger(__name__)

chatbot_router = APIRouter()
chatbot_controller = ChatbotController()

class ChatRequest(BaseModel):
    conversation_id: str
    user_input: str

@chatbot_router.get("/chat-history", tags=["Chatbot"])
def chat_history(conversation_id: str):
    """Return the history for a specific conversation."""
    return chatbot_controller.get_history(conversation_id)

@chatbot_router.post("/v1/chat", tags=["Chatbot"])
async def chat(
    request: ChatRequest,
    authorization: str = Header(...),
):
    """
    Non-streaming chat with tool-call support.
    The patient JWT is passed as the Authorization header.
    """
    try:
        reply = await chatbot_controller.run_turn(
            request.conversation_id, request.user_input, authorization
        )
        return {"response": reply}

    except HTTPException:
        raise
    except Exception as exc:
        logging.error(f"Error in /v1/chat: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

@chatbot_router.post("/v1/chat/stream", tags=["Chatbot"])
async def chat_stream(
    request: ChatRequest,
    authorization: str = Header(...),
):
    """
    SSE streaming chat.
    Tool calls are resolved synchronously before streaming begins,
    then the final text is streamed word-by-word.
    """
    async def event_generator():
        try:
            # Resolve all tool calls first, get final reply text
            reply = await chatbot_controller.run_turn(
                request.conversation_id, request.user_input, authorization
            )

            # Stream the reply as word-level deltas
            words = reply.split(" ")
            for i, word in enumerate(words):
                chunk = word if i == 0 else " " + word
                yield sse("delta", {"text": chunk})

            yield sse("done", {"response": reply})

        except Exception as exc:
            logging.error(f"Error in /v1/chat/stream: {exc}")
            yield sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
