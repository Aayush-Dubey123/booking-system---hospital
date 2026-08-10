import client from './client'

/**
 * Sends a standard (non-streaming) message to the chatbot.
 * The Bearer token (JWT) is automatically appended by the `client` interceptor.
 */
export async function sendChatMessage(conversationId, userInput) {
  const response = await client.post('/v1/chat', {
    conversation_id: conversationId,
    user_input: userInput,
  })
  return response.data.response
}

/**
 * Gets conversation history (if implemented for the frontend).
 */
export async function getChatHistory(conversationId) {
  const response = await client.get('/chat-history', {
    params: { conversation_id: conversationId },
  })
  return response.data
}
