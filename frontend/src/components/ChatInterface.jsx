import { useState, useRef, useEffect } from 'react'

function ChatInterface({ llmProvider, llmModel, initialContext }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: 'Hello! Ask me any question about your data.' }
    ])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef(null)

    useEffect(() => {
        if (initialContext?.table_name) {
            setInput(`Tell me about the ${initialContext.table_name} table.`)
        }
    }, [initialContext])

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
            // Use QnA Endpoint
            const res = await fetch('/api/v1/qna', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: userMessage.text,
                    model_provider: llmProvider,
                    model_name: llmModel
                })
            })

            if (!res.ok) {
                const errText = await res.text()
                throw new Error(errText || 'Failed to fetch response')
            }

            const data = await res.json()

            const botMessage = {
                role: 'assistant',
                text: data.summary, // Main answer
                details: {
                    business: data.business_explanation,
                    entities: data.entity_explanation,
                    sql: data.sql_query,
                    table_layout: data.table_layout,
                    data: data.data
                },
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
            <div className="card chat-window" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <div className="messages" style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message ${msg.role}`} style={{ marginBottom: '20px', maxWidth: '85%', alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', marginLeft: msg.role === 'user' ? 'auto' : 0 }}>
                            <div style={{
                                padding: '12px 16px',
                                borderRadius: '12px',
                                background: msg.role === 'user' ? '#3b82f6' : 'rgba(255,255,255,0.05)',
                                color: 'white',
                                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                            }}>
                                <div>{msg.text}</div>
                            </div>

                            {/* Render Details if available (Assistant only) */}
                            {msg.details && (
                                <div className="message-details" style={{ marginTop: '8px', marginLeft: '10px', fontSize: '0.9rem' }}>
                                    <details style={{ cursor: 'pointer' }}>
                                        <summary style={{ color: '#94a3b8', userSelect: 'none' }}>💡 View Analysis & SQL</summary>
                                        <div style={{ marginTop: '10px', padding: '10px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}>

                                            <div style={{ marginBottom: '10px' }}>
                                                <strong style={{ color: '#a5b4fc' }}>Business Context:</strong>
                                                <div style={{ color: '#cbd5e1', marginTop: '4px' }}>{msg.details.business}</div>
                                            </div>

                                            <div style={{ marginBottom: '10px' }}>
                                                <strong style={{ color: '#86efac' }}>Entities Used:</strong>
                                                <div style={{ color: '#cbd5e1', marginTop: '4px' }}>{msg.details.entities}</div>
                                            </div>

                                            <div style={{ marginBottom: '10px' }}>
                                                <strong style={{ color: '#fca5a5' }}>SQL Query:</strong>
                                                <pre style={{ background: '#0f172a', padding: '8px', borderRadius: '4px', overflowX: 'auto', marginTop: '4px', fontSize: '0.85rem' }}>
                                                    <code>{msg.details.sql}</code>
                                                </pre>
                                            </div>

                                            {msg.details.data && msg.details.data.length > 0 && (
                                                <div style={{ marginBottom: '10px' }}>
                                                    <strong style={{ color: '#f0abfc' }}>Result Data ({msg.details.data.length} rows):</strong>
                                                    <div style={{ maxHeight: '150px', overflow: 'auto', marginTop: '4px', background: '#0f172a', borderRadius: '4px' }}>
                                                        <table style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse' }}>
                                                            <thead>
                                                                <tr>
                                                                    {Object.keys(msg.details.data[0]).map(k => (
                                                                        <th key={k} style={{ padding: '4px 8px', textAlign: 'left', borderBottom: '1px solid #334155', color: '#94a3b8' }}>{k}</th>
                                                                    ))}
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                {msg.details.data.map((row, r_idx) => (
                                                                    <tr key={r_idx}>
                                                                        {Object.values(row).map((val, c_idx) => (
                                                                            <td key={c_idx} style={{ padding: '4px 8px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>{String(val)}</td>
                                                                        ))}
                                                                    </tr>
                                                                ))}
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </details>
                                </div>
                            )}
                        </div>
                    ))}
                    {isLoading && (
                        <div className="message assistant" style={{ color: '#94a3b8', fontStyle: 'italic' }}>
                            <span className="typing-dot">...</span> Analyzing data ({llmProvider})...
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area" style={{ padding: '20px', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '10px' }}>
                    <input
                        type="text"
                        placeholder="Type your question here..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={isLoading}
                        style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'rgba(255,255,255,0.05)', color: 'white' }}
                    />
                    <button
                        className="btn-primary"
                        onClick={sendQuery}
                        disabled={isLoading}
                        style={{ width: '100px' }}
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    )
}

export default ChatInterface
