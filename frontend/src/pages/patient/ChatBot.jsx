import { useState, useRef, useEffect, useCallback } from 'react'
import Layout from '../../components/Layout'
import { sendChatMessage } from '../../api/chatbotApi'

/* ─── Session-based conversation ID ─── */
function getOrCreateConversationId() {
  let id = sessionStorage.getItem('cc_conv_id')
  if (!id) {
    id = crypto.randomUUID()
    sessionStorage.setItem('cc_conv_id', id)
  }
  return id
}

/* ─── Simple Time Formatter ─── */
function fmtTime(date) {
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

const WELCOME_MESSAGE = {
  role: 'bot',
  text: "Hello! I am the CityCare Appointment Assistant.\n\nI can help you check available slots, book a new appointment, and view your existing appointments. How can I help you today?",
  ts: new Date(),
}

export default function ChatBot() {
  const conversationId = useRef(getOrCreateConversationId()).current
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const send = useCallback(async (text) => {
    const trimmed = (text ?? input).trim()
    if (!trimmed || isTyping) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: trimmed, ts: new Date() }])
    setIsTyping(true)

    try {
      const reply = await sendChatMessage(conversationId, trimmed)
      setMessages(prev => [...prev, { role: 'bot', text: reply, ts: new Date() }])
    } catch (err) {
      const msg = err?.response?.data?.detail ?? err.message ?? 'Something went wrong.'
      setMessages(prev => [...prev, {
        role: 'bot',
        text: `Error: ${msg}\nPlease try again.`,
        ts: new Date(),
      }])
    } finally {
      setIsTyping(false)
      inputRef.current?.focus()
    }
  }, [input, isTyping, conversationId])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  const clearChat = () => {
    sessionStorage.removeItem('cc_conv_id')
    const newId = crypto.randomUUID()
    sessionStorage.setItem('cc_conv_id', newId)
    setMessages([{ ...WELCOME_MESSAGE, ts: new Date() }])
    inputRef.current?.focus()
  }

  return (
    <Layout>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', maxWidth: '800px', margin: '0 auto', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden', backgroundColor: '#fff' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', borderBottom: '1px solid #e2e8f0', backgroundColor: '#f8fafc' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#1e293b' }}>AI Appointment Assistant</h2>
            <p style={{ margin: 0, fontSize: '13px', color: '#64748b' }}>Powered by Gemini</p>
          </div>
          <button onClick={clearChat} style={{ background: 'transparent', border: '1px solid #cbd5e1', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '13px', color: '#475569' }}>
            Clear Chat
          </button>
        </div>

        {/* Message Area */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px', backgroundColor: '#fcfcfc', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {messages.map((msg, idx) => {
            const isBot = msg.role === 'bot'
            return (
              <div key={idx} style={{ display: 'flex', flexDirection: isBot ? 'row' : 'row-reverse', alignItems: 'flex-start', gap: '12px' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: isBot ? '#0E6E5C' : '#334155', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 'bold', flexShrink: 0 }}>
                  {isBot ? 'AI' : 'You'}
                </div>
                <div style={{ maxWidth: '75%', display: 'flex', flexDirection: 'column', alignItems: isBot ? 'flex-start' : 'flex-end', gap: '4px' }}>
                  <div style={{
                    padding: '12px 16px',
                    borderRadius: '6px',
                    backgroundColor: isBot ? '#f1f5f9' : '#0E6E5C',
                    color: isBot ? '#1e293b' : '#ffffff',
                    border: isBot ? '1px solid #e2e8f0' : 'none',
                    fontSize: '14px',
                    lineHeight: '1.5',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}>
                    {msg.text}
                  </div>
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>{fmtTime(msg.ts)}</span>
                </div>
              </div>
            )
          })}
          
          {/* Subtle Typing Indicator */}
          {isTyping && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#0E6E5C', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 'bold' }}>AI</div>
              <div style={{ padding: '8px 12px', borderRadius: '6px', backgroundColor: '#f1f5f9', border: '1px solid #e2e8f0', fontSize: '13px', color: '#64748b' }}>
                Typing...
              </div>
            </div>
          )}
          
          <div ref={bottomRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: '16px', borderTop: '1px solid #e2e8f0', backgroundColor: '#fff', display: 'flex', gap: '12px' }}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message here... (Press Enter to send)"
            style={{
              flex: 1,
              resize: 'none',
              padding: '12px',
              border: '1px solid #cbd5e1',
              borderRadius: '4px',
              fontFamily: 'inherit',
              fontSize: '14px',
              height: '48px',
              maxHeight: '120px',
              outline: 'none',
            }}
          />
          <button
            onClick={() => send()}
            disabled={!input.trim() || isTyping}
            style={{
              padding: '0 20px',
              backgroundColor: '#0E6E5C',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              fontWeight: '600',
              cursor: (!input.trim() || isTyping) ? 'not-allowed' : 'pointer',
              opacity: (!input.trim() || isTyping) ? 0.6 : 1,
            }}
          >
            Send
          </button>
        </div>
      </div>
    </Layout>
  )
}
