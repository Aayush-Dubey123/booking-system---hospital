import json
import os
import httpx
from fastapi import APIRouter, Header, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError

# pyrefly: ignore [missing-import]
from core.controllers.chatbot_controller import ChatbotController
# pyrefly: ignore [missing-import]
from common.logger import logger
# pyrefly: ignore [missing-import]
from core.apis.schemas.requests.telegram_request import TelegramUpdate

logging = logger(__name__)

# Load and verify TELEGRAM_BOT_TOKEN from environment variables
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
if not telegram_bot_token:
    logging.warning("TELEGRAM_BOT_TOKEN environment variable is not set. Telegram webhook integration may not function correctly.")

chatbot_router = APIRouter()
chatbot_controller = ChatbotController()

async def send_telegram_message(chat_id: int | str, text: str):
    """Sends a message back to the Telegram chat using the Bot API."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.error("TELEGRAM_BOT_TOKEN is not configured. Cannot send Telegram reply.")
        return
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=10.0)
            if resp.status_code != 200:
                logging.error(f"Failed to send Telegram message: {resp.status_code} - {resp.text}")
            else:
                logging.info(f"Successfully sent Telegram reply to chat_id={chat_id}")
    except Exception as exc:
        logging.error(f"Error sending Telegram message: {exc}")


async def process_telegram_update(payload: dict):
    """Processes the Telegram message asynchronously via the AI Agent and sends a reply."""
    try:
        update = TelegramUpdate.model_validate(payload)
        message = update.message or update.edited_message
        if message and message.text:
            chat_id = message.chat.id
            text = message.text
            
            # Pass to the AI agent / ChatbotController
            reply = await chatbot_controller.run_telegram_turn(str(chat_id), text)
            
            # Send the final response back to Telegram
            if reply:
                await send_telegram_message(chat_id, reply)
    except Exception as exc:
        logging.error(f"Error in process_telegram_update background worker: {exc}")


@chatbot_router.post("/telegram/webhook", tags=["Chatbot"])
async def telegram_webhook(payload: dict, background_tasks: BackgroundTasks):
    """
    Telegram Bot API webhook endpoint.
    Accepts update payloads, validates structure, logs non-sensitive details,
    enqueues processing as a background task, and returns 200 immediately.
    """
    try:
        # Validate the incoming payload against our Pydantic model
        update = TelegramUpdate.model_validate(payload)
        
        # Safely parse text and chat information
        message = update.message or update.edited_message
        if message:
            chat_id = message.chat.id
            chat_type = message.chat.type
            message_id = message.message_id
            
            # Log non-sensitive information
            user_info = ""
            if message.from_user:
                user_info = f", user_id={message.from_user.id}"
                if message.from_user.username:
                    user_info += f", username={message.from_user.username}"
            
            text_length = len(message.text) if message.text else 0
            has_text = message.text is not None
            
            logging.info(
                f"[Telegram Webhook] Enqueued update_id={update.update_id}, "
                f"chat_id={chat_id} (type={chat_type}), message_id={message_id}"
                f"{user_info}, has_text={has_text}, text_length={text_length}"
            )
            
            # Enqueue background task
            background_tasks.add_task(process_telegram_update, payload)
        else:
            logging.info(f"[Telegram Webhook] Received non-message update_id={update.update_id}")
            
        return {"ok": True, "status": "processed"}
        
    except ValidationError as err:
        # Log validation error, but return HTTP 200 with error details to satisfy Telegram requirements
        logging.warning(f"[Telegram Webhook] Validation failed: {err}")
        return {
            "ok": False,
            "error": "Validation failed",
            "details": err.errors()
        }
        
    except Exception as exc:
        logging.error(f"[Telegram Webhook] Error processing update: {exc}")
        return {
            "ok": False,
            "error": "Internal server error"
        }

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
