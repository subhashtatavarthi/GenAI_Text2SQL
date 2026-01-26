import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown' // Should have instealled this, but for now just raw text or pre

function ChatInterface({ llmProvider, llmModel }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: 'Hello! Ask me any question about your data.' }
    ])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(scrollToBottom, [messages])

    const sendQuery = async () => {
        if (!input.trim()) return

        const userMessage = { role: 'user', text: input }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setIsLoading(true)

        try {
            const res = await fetch('/api/v1/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: userMessage.text,
                    model_provider: llmProvider,
                    model_name: llmModel
                })
            })


            if (!res.ok) {
                throw new Error('Failed to fetch response')
            }

            const data = await res.json()

            let responseText = ""
            if (data.error) {
                responseText = `⚠️ Error: ${data.error}`
            } else {
                responseText = data.answer
            }

            const botMessage = {
                role: 'assistant',
                text: responseText,
                sql: data.sql_query,
                error: data.error
            }

            setMessages(prev => [...prev, botMessage])

        } catch (e) {
            setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${e.message}`, error: true }])
        } finally {
            setIsLoading(false)
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') sendQuery()
    }

    return (
        <div className="chat-interface">
            <div className="card chat-window">
                <div className="messages">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message ${msg.role}`}>
                            <div>{msg.text}</div>

                            {msg.sql && (
                                <div className="sql-block">
                                    <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '4px' }}>GENERATED SQL</div>
                                    <code>{msg.sql}</code>
                                </div>
                            )}
                        </div>
                    ))}
                    {isLoading && (
                        <div className="message assistant">
                            <span className="typing-dot">...</span> Thinking ({llmProvider})
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area">
                    <input
                        type="text"
                        placeholder="Type your question here (e.g., 'What are the top 3 items?')..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={isLoading}
                    />
                    <button
                        className="btn-primary"
                        onClick={sendQuery}
                        disabled={isLoading}
                        style={{ width: '80px' }}
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    )
}

export default ChatInterface
