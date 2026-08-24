# Chatbot API Documentation

## Overview

The chatbot API provides three main endpoints for managing patient conversations and retrieving chat history.

## Authentication

All endpoints (except health check) require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <jwt-token>
```

The JWT token must contain:
- `id` or `user_id`: Patient/User ID
- `role`: Must be "patient" for chatbot access
- `exp`: Expiration timestamp

## Endpoints

### 1. POST /v1/chat

**Description:** Send a message to the chatbot and receive a non-streaming response.

**Request:**
```json
{
  "conversation_id": "user123-session1",
  "user_input": "What are my appointments?"
}
```

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "response": "You have 2 upcoming appointments:\n\n1. General Checkup - Aug 20, 2024 at 10:00 AM\n2. Follow-up - Aug 25, 2024 at 2:00 PM"
}
```

**Error Responses:**

| Status | Error | Cause |
|--------|-------|-------|
| 401 | Invalid authentication credentials | Missing or invalid JWT |
| 403 | This operation requires patient role | User is not a patient |
| 500 | Error message | Server error (check logs) |

**cURL Example:**
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user123",
    "user_input": "Check my appointments"
  }'
```

**JavaScript/Fetch Example:**
```javascript
const response = await fetch('/v1/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    conversation_id: userId,
    user_input: userMessage
  })
});
const data = await response.json();
console.log(data.response);
```

---

### 2. POST /v1/chat/stream

**Description:** Send a message and receive a streaming response using Server-Sent Events (SSE).

**Request:**
```json
{
  "conversation_id": "user123-session1",
  "user_input": "Tell me about my prescription"
}
```

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
Accept: text/event-stream
```

**Response (200 OK) - Server-Sent Events:**
```
event: delta
data: {"text": "You"}

event: delta
data: {"text": " have"}

event: delta
data: {"text": " a"}

event: delta
data: {"text": " prescription"}

event: delta
data: {"text": " for"}

event: delta
data: {"text": " Amoxicillin"}

event: done
data: {"response": "You have a prescription for Amoxicillin, 500mg, take twice daily for 7 days."}
```

**Error Responses:** Same as /v1/chat

**JavaScript Example:**
```javascript
async function streamChat(message) {
  const response = await fetch('/v1/chat/stream', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      conversation_id: userId,
      user_input: message
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullResponse = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value, { stream: true });
    const lines = text.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const json = JSON.parse(line.substring(6));
          if (json.text) {
            console.log(json.text); // Print as it streams
            fullResponse += json.text;
          }
          if (json.response) {
            console.log('Complete:', json.response);
          }
        } catch (e) {
          // Ignore parsing errors for comments/empty lines
        }
      }
    }
  }

  return fullResponse;
}
```

---

### 3. GET /chat-history

**Description:** Retrieve the conversation history for a specific conversation ID.

**Query Parameters:**
```
conversation_id=user123-session1
```

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response (200 OK):**
```json
[
  {
    "role": "user",
    "parts": [
      {
        "type": "text",
        "text": "What are my upcoming appointments?"
      }
    ]
  },
  {
    "role": "assistant",
    "parts": [
      {
        "type": "text",
        "text": "You have 2 upcoming appointments..."
      }
    ]
  },
  {
    "role": "user",
    "parts": [
      {
        "type": "text",
        "text": "Can I book another one?"
      }
    ]
  },
  {
    "role": "assistant",
    "parts": [
      {
        "type": "function_call",
        "name": "get_available_slots",
        "args": {
          "appointment_date": "2024-08-20",
          "hospital_id": null
        }
      }
    ]
  }
]
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/chat-history?conversation_id=user123" \
  -H "Authorization: Bearer your-jwt-token"
```

---

## Chatbot Capabilities

### Available Tools

The chatbot can execute the following operations:

#### 1. get_available_slots
Retrieves available appointment slots for a given date.

**Parameters:**
- `appointment_date` (string, required): Date in YYYY-MM-DD format
- `hospital_id` (string, optional): Filter by specific hospital

**Example Response:**
```json
{
  "appointment_date": "2024-08-20",
  "slots": ["10:00", "11:00", "14:00", "15:30"],
  "hospital_id": "hospital123"
}
```

#### 2. book_appointment
Books an appointment for the authenticated patient.

**Parameters:**
- `hospital_id` (string, required): Hospital ID
- `appointment_date` (string, required): Date in YYYY-MM-DD format
- `slot` (string, required): Time slot (e.g., "10:00")
- `reason` (string, required): Reason for appointment
- `symptoms` (string, required): Patient symptoms
- `temperature` (number, required): Body temperature in Celsius

**Example Response:**
```json
{
  "id": "appt123",
  "appointment_date": "2024-08-20",
  "slot": "10:00",
  "reason": "General Checkup",
  "symptoms": "Sore throat",
  "temperature": 37.5,
  "status": "confirmed"
}
```

#### 3. my_appointments
Retrieves all appointments for the authenticated patient.

**Parameters:** None

**Example Response:**
```json
{
  "appointments": [
    {
      "id": "appt123",
      "appointment_date": "2024-08-20",
      "slot": "10:00",
      "reason": "General Checkup",
      "status": "confirmed"
    },
    {
      "id": "appt456",
      "appointment_date": "2024-08-25",
      "slot": "14:00",
      "reason": "Follow-up",
      "status": "pending"
    }
  ]
}
```

#### 4. get_prescription_info
Retrieves prescription information using RAG (Retrieval-Augmented Generation).

**Parameters:**
- `query` (string, required): What information to retrieve (e.g., "dosage", "medicines")

**Example Response:**
```json
{
  "prescription_context": "Prescription Summary:\nPrescription ID: rx789\nPatient Name: John Doe\nDoctor Name: Dr. Jane Smith\nDiagnosis: Bacterial Infection\nPrescribed Medicines & Dosage: Amoxicillin 500mg, take twice daily for 7 days\nSpecial Notes/Instructions: Take with food, avoid dairy products"
}
```

---

## Sample Conversations

### Example 1: Checking Appointments

**User:** "What are my upcoming appointments?"

**Chatbot:** "Let me check your appointments for you..."
*Executes: `my_appointments`*

"You have 2 upcoming appointments:
1. General Checkup - August 20, 2024 at 10:00 AM with Dr. Johnson at Central Hospital
2. Follow-up Visit - August 25, 2024 at 2:00 PM with Dr. Smith at West Medical Center

Would you like to book an additional appointment or need any other information?"

### Example 2: Booking an Appointment

**User:** "I'd like to book an appointment for next week"

**Chatbot:** "I'd be happy to help you book an appointment. Let me start by checking available dates..."

**User:** "August 28th"

**Chatbot:** "Let me check available slots for August 28th..."
*Executes: `get_available_slots` with date "2024-08-28"*

"Great! Here are the available time slots on August 28th:
- 09:00 AM
- 10:30 AM
- 02:00 PM
- 03:30 PM

Which time works best for you?"

**User:** "10:30 AM"

**Chatbot:** "Perfect! I'll need a few more details:
- What hospital would you prefer?
- What's the reason for your visit?
- Any symptoms you're experiencing?
- Your current body temperature?"

### Example 3: Prescription Inquiry

**User:** "Can you tell me about my prescribed medicines?"

**Chatbot:** "Let me retrieve your prescription information..."
*Executes: `get_prescription_info` with query "medicines dosage"*

"Based on your prescriptions, you have:

**Amoxicillin 500mg**
- Dosage: Take twice daily (every 12 hours)
- Duration: 7 days
- Instructions: Take with food to minimize stomach upset
- Important: Avoid dairy products for 2 hours after taking the medication

**Ibuprofen 400mg**
- As needed for pain relief
- Maximum 3 times daily
- Take with or after meals

Is there anything else you'd like to know about your prescriptions?"

---

## Error Handling

### Common Error Scenarios

| Scenario | Status | Error Message | Solution |
|----------|--------|---------------|----------|
| Missing JWT | 401 | "Invalid authentication credentials" | Include valid JWT in Authorization header |
| Invalid JWT | 401 | "Invalid authentication credentials" | Refresh JWT token |
| User not patient | 403 | "This operation requires patient role" | Ensure user has "patient" role in JWT |
| Ollama offline | 500 | "Error generating embedding with Ollama" | Start Ollama service |
| MongoDB down | 500 | "Error in RAG search" | Ensure MongoDB is running |
| Invalid input | 400 | "Pydantic validation error" | Check request format |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting & Performance

### Recommended Limits (per user/IP)

- **Requests per minute:** 30
- **Concurrent conversations:** 5
- **Message size limit:** 10,000 characters

### Response Times

- **Regular chat:** 1-3 seconds (depends on Gemini API)
- **Streaming chat:** First token in < 500ms, subsequent < 100ms
- **History retrieval:** < 100ms

---

## Security Considerations

1. **Always use HTTPS** in production
2. **Validate JWT tokens** before processing requests
3. **Sanitize user input** (though Pydantic helps)
4. **Monitor for prompt injection** in user messages
5. **Rate limit** to prevent abuse
6. **Log** all interactions for audit trails
7. **Rotate secrets** regularly

---

## Webhook Events (Future)

Currently not implemented, but the architecture supports:
- `appointment.booked`
- `prescription.indexed`
- `conversation.created`
- `conversation.completed`

---

## API Versioning

Current version: **v1**

Endpoints use `/v1/` prefix. Future versions (v2, v3) will be additive.

---

## Support

For issues:
1. Check authentication is correct
2. Verify external services (Ollama, MongoDB, Gemini API) are running
3. Review error message in response
4. Check server logs for detailed errors
5. See MIGRATION_GUIDE.md for troubleshooting
