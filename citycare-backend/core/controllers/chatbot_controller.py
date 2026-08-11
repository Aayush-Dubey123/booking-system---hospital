import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

from google import genai
from google.genai import types as genai_types
from common.logger import logger
from common.auth_helpers import verify_token, require_role
from fastapi import HTTPException, status
from core.controllers.appointment_controller import AppointmentController

logging = logger(__name__)

# Load .env from citycare-backend directory
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

api_key = os.environ.get("API_KEY")
if not api_key:
    logging.warning("API_KEY environment variable is not set. Chatbot will not work.")

# Build the async Gemini client (google-genai SDK v2)
_gemini_client = genai.Client(api_key=api_key)

# ---------------------------------------------------------------------------
# Per-conversation in-memory store
# Key = conversation_id, Value = list of genai_types.Content
# ---------------------------------------------------------------------------
conversations: dict[str, list] = {}

# ---------------------------------------------------------------------------
# System instruction
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """\
You are CityCare Patient Assistant, a friendly and concise appointment and medical helper.

## Your purpose
Help patients with:
- Checking available appointment slots
- Booking appointments
- Viewing their existing appointments
- Answering questions about their prescribed medicines, dosages, diagnosis, and medical instructions

## Rules
- Always use the provided tools to get live data. Never invent slots, dates, doctors, hospitals, appointment IDs, or prescription details.
- For any questions about prescriptions, medicines, dosages, diagnosis, or treatment instructions, ALWAYS use the get_prescription_info tool.
- CRITICAL SECURITY RULE: If get_prescription_info returns no prescription records or no matching medical information for the patient, you MUST state clearly: "No prescription records or matching medical information are available for your account." Do NOT provide generic medical advice, do NOT guess dosages, and do NOT repeat or confirm any medicine names or patient IDs mentioned in the user prompt.
- Before booking, collect all required information: hospital_id, appointment_date, slot, reason, symptoms, temperature.
  Ask for missing fields one at a time — do not overwhelm the patient.
- Confirm a booking ONLY after the book_appointment tool returns successfully. If it fails, explain the actual error.
- For my_appointments and get_prescription_info, identity is securely retrieved from their login token.
- Never reveal or guess another patient's information.
- Do not diagnose new medical conditions. If asked for medical advice on new symptoms, say: "I can help you book an appointment with a doctor for proper advice."
- Keep responses short, accurate, and friendly.
- If you need a hospital_id and the patient has not provided it, ask them.
"""

# ---------------------------------------------------------------------------
# Tool declarations for Gemini
# ---------------------------------------------------------------------------
TOOL_DECLARATIONS = genai_types.Tool(
    function_declarations=[
        genai_types.FunctionDeclaration(
            name="get_available_slots",
            description="Get available appointment slots for a given date at a hospital. Call this before presenting slot options. Never invent slots.",
            parameters=genai_types.Schema(
                type=genai_types.Type.OBJECT,
                properties={
                    "appointment_date": genai_types.Schema(
                        type=genai_types.Type.STRING,
                        description="Date in YYYY-MM-DD format, e.g. 2024-08-15",
                    ),
                    "hospital_id": genai_types.Schema(
                        type=genai_types.Type.STRING,
                        description="Optional hospital ID to scope the check",
                    ),
                },
                required=["appointment_date"],
            ),
        ),
        genai_types.FunctionDeclaration(
            name="book_appointment",
            description="Book an appointment for the authenticated patient. Never claim success until this tool returns without an error.",
            parameters=genai_types.Schema(
                type=genai_types.Type.OBJECT,
                properties={
                    "hospital_id": genai_types.Schema(
                        type=genai_types.Type.STRING,
                        description="Hospital ID",
                    ),
                    "appointment_date": genai_types.Schema(
                        type=genai_types.Type.STRING,
                        description="Date in YYYY-MM-DD format",
                    ),
                    "slot": genai_types.Schema(
                        type=genai_types.Type.STRING,
                        description="Time slot e.g. 10:00 or 17:30",
                    ),
                    "reason": genai_types.Schema(
                        type=genai_types.Type.STRING,
                        description="Reason for the appointment",
                    ),
                    "symptoms": genai_types.Schema(
                        type=genai_types.Type.STRING,
                        description="Patient symptoms",
                    ),
                    "temperature": genai_types.Schema(
                        type=genai_types.Type.NUMBER,
                        description="Body temperature in Celsius. Use 37.0 if not provided.",
                    ),
                },
                required=["hospital_id", "appointment_date", "slot", "reason", "symptoms", "temperature"],
            ),
        ),
        genai_types.FunctionDeclaration(
            name="my_appointments",
            description="Retrieve all appointments of the authenticated patient. Identity comes from the JWT token.",
            parameters=genai_types.Schema(
                type=genai_types.Type.OBJECT,
                properties={},
                required=[],
            ),
        ),
        genai_types.FunctionDeclaration(
            name="get_prescription_info",
            description="Retrieve prescribed medicines, dosage, diagnosis, or special instructions from the patient's prescriptions. Call this whenever the patient asks about their prescription, medication, dosage, or medical notes.",
            parameters=genai_types.Schema(
                type=genai_types.Type.OBJECT,
                properties={
                    "query": genai_types.Schema(
                        type=genai_types.Type.STRING,
                        description="Query describing the prescription or medicine information requested by the patient.",
                    ),
                },
                required=["query"],
            ),
        ),
    ]
)

GENERATE_CONFIG = genai_types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    tools=[TOOL_DECLARATIONS],
    tool_config=genai_types.ToolConfig(
        function_calling_config=genai_types.FunctionCallingConfig(
            mode=genai_types.FunctionCallingConfigMode.AUTO,
        )
    ),
)


class ChatbotController:
    """Controller for processing Gemini Chatbot requests and routing tools."""

    def __init__(self) -> None:
        self.appointment_controller = AppointmentController()

    async def _execute_tool(self, tool_name: str, args: dict, authorization: str) -> dict:
        """Dispatcher for tool calls to exact existing AppointmentController methods and RAGService."""
        try:
            if tool_name == "get_available_slots":
                appointment_date = date.fromisoformat(args["appointment_date"])
                hospital_id = args.get("hospital_id")

                result = await self.appointment_controller.get_schedule(
                    appointment_date, hospital_id
                )
                result["appointment_date"] = str(result["appointment_date"])
                return result

            elif tool_name == "book_appointment":
                request_data = {
                    "hospital_id": args["hospital_id"],
                    "appointment_date": date.fromisoformat(args["appointment_date"]),
                    "slot": args["slot"],
                    "reason": args["reason"],
                    "symptoms": args["symptoms"],
                    "temperature": float(args["temperature"]),
                }
                result = await self.appointment_controller.book_appointment(
                    request_data, authorization
                )
                if "appointment_date" in result and hasattr(result["appointment_date"], "isoformat"):
                    result["appointment_date"] = result["appointment_date"].isoformat()
                return result

            elif tool_name == "my_appointments":
                results = await self.appointment_controller.get_my_appointments(authorization)
                serializable = []
                for appt in results:
                    appt_copy = dict(appt)
                    for key in ("appointment_date", "created_at"):
                        if key in appt_copy and hasattr(appt_copy[key], "isoformat"):
                            appt_copy[key] = appt_copy[key].isoformat()
                    serializable.append(appt_copy)
                return {"appointments": serializable}

            elif tool_name == "get_prescription_info":
                payload = verify_token(authorization)
                patient_id = payload["id"]
                query = args.get("query", "")

                from core.services.rag_service import RAGService
                rag_results = await RAGService().search_prescriptions(
                    patient_id=patient_id, query=query, top_k=3, similarity_threshold=0.4
                )

                if not rag_results:
                    return {"result": "No prescription records or matching medical information available for this authenticated patient."}

                chunks = [r["text"] for r in rag_results]
                return {"prescription_context": "\n---\n".join(chunks)}

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except HTTPException as exc:
            logging.error(f"HTTP error executing tool {tool_name}: {exc.detail}")
            return {"error": exc.detail}
        except Exception as exc:
            logging.error(f"Error executing tool {tool_name}: {exc}")
            return {"error": str(exc)}

    async def run_turn(self, conversation_id: str, user_text: str, authorization: str) -> str:
        """
        Runs one chat turn: appends user input, calls Gemini, resolves function calls, returns final text.
        """
        payload = verify_token(authorization)
        require_role(payload, "patient")

        if conversation_id not in conversations:
            conversations[conversation_id] = []

        history = conversations[conversation_id]

        user_content = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=user_text)],
        )
        contents = history + [user_content]

        response = await _gemini_client.aio.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=GENERATE_CONFIG,
        )

        history.append(user_content)

        # Function calling loop
        while True:
            fc_list = []
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.function_call:
                                fc_list.append(part.function_call)

            if not fc_list:
                break

            if response.candidates and response.candidates[0].content:
                history.append(response.candidates[0].content)

            tool_response_parts = []
            for fc in fc_list:
                tool_name = fc.name
                args = dict(fc.args) if fc.args else {}

                logging.info(f"Chatbot invoking tool '{tool_name}'")
                tool_result = await self._execute_tool(tool_name, args, authorization)

                tool_response_parts.append(
                    genai_types.Part(
                        function_response=genai_types.FunctionResponse(
                            name=tool_name,
                            response={"result": tool_result},
                        )
                    )
                )

            tool_content = genai_types.Content(role="user", parts=tool_response_parts)
            history.append(tool_content)

            response = await _gemini_client.aio.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=history[:],
                config=GENERATE_CONFIG,
            )

        final_text = response.text if response.text else ""

        if response.candidates and response.candidates[0].content:
            history.append(response.candidates[0].content)

        return final_text

    def get_history(self, conversation_id: str) -> list:
        raw = conversations.get(conversation_id, [])
        result = []
        for content in raw:
            if not content or not content.parts:
                continue
            parts_out = []
            for part in content.parts:
                if part.text:
                    parts_out.append({"type": "text", "text": part.text})
                elif part.function_call:
                    parts_out.append({
                        "type": "function_call",
                        "name": part.function_call.name,
                        "args": dict(part.function_call.args) if part.function_call.args else {},
                    })
                elif part.function_response:
                    parts_out.append({
                        "type": "function_response",
                        "name": part.function_response.name,
                    })
            result.append({"role": content.role, "parts": parts_out})
        return result
