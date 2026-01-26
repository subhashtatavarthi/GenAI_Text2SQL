import { useState } from 'react'

function ConnectionPanel({ onConnect, setLlmProvider, currentLlm }) {
    const [dbType, setDbType] = useState('sqlite')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')

    // Server config (Allow custom backend URL for deployed frontend)
    const [serverUrl, setServerUrl] = useState('')

    // Form State
    const [sqlitePath, setSqlitePath] = useState('sales.db')
    const [pgHost, setPgHost] = useState('localhost')
    const [pgPort, setPgPort] = useState(5432)
    const [pgUser, setPgUser] = useState('postgres')
    const [pgPass, setPgPass] = useState('password')
    const [pgDb, setPgDb] = useState('sales_db')

    const handleConnect = async () => {
        setIsLoading(true)
        setError('')

        // Determine base URL (if empty, use default relative path which uses proxy)
        const baseUrl = serverUrl.replace(/\/$/, '') || ''

        const payload = {
            type: dbType,
            details: {}
        }

        if (dbType === 'sqlite') {
            payload.details = { file_path: sqlitePath }
        } else {
            payload.details = {
                host: pgHost,
                port: Number(pgPort),
                username: pgUser,
                password: pgPass,
                database: pgDb
            }
        }

        try {
            const res = await fetch(`${baseUrl}/api/v1/get-schema`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })

            if (!res.ok) {
                const err = await res.json()
                throw new Error(err.detail || 'Failed to connect')
            }

            const data = await res.json()
            // Pass the URL to parent so ChatInterface can use it too
            onConnect(payload, data, baseUrl)

        } catch (e) {
            setError(e.message)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="connection-panel">
            <div className="form-group" style={{ marginBottom: '16px' }}>
                <label>Backend API URL</label>
                <input
                    type="text"
                    placeholder="Leave empty for localhost..."
                    value={serverUrl}
                    onChange={(e) => setServerUrl(e.target.value)}
                    style={{ fontSize: '0.85rem' }}
                />
                <small style={{ color: 'var(--text-secondary)', fontSize: '0.7rem' }}>
                    Required if using GitHub Pages (e.g. ngrok or cloud URL)
                </small>
            </div>
            <div className="form-group">
                <label>LLM Provider</label>
                <select value={currentLlm} onChange={(e) => setLlmProvider(e.target.value)}>
                    <option value="openai">OpenAI (GPT-3.5)</option>
                    <option value="gemini">Google Gemini 2.0</option>
                </select>
            </div>

            <hr style={{ borderColor: 'var(--border-color)', margin: '16px 0' }} />

            <div className="form-group" style={{ marginBottom: '16px' }}>
                <label>Database Type</label>
                <select value={dbType} onChange={(e) => setDbType(e.target.value)}>
                    <option value="sqlite">SQLite (Local File)</option>
                    <option value="postgres">PostgreSQL</option>
                </select>
            </div>

            {dbType === 'sqlite' ? (
                <div className="form-group">
                    <label>File Path</label>
                    <input
                        type="text"
                        value={sqlitePath}
                        onChange={(e) => setSqlitePath(e.target.value)}
                    />
                </div>
            ) : (
                <div className="pg-form" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div className="form-group">
                        <label>Host</label>
                        <input type="text" value={pgHost} onChange={(e) => setPgHost(e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label>Port</label>
                        <input type="number" value={pgPort} onChange={(e) => setPgPort(e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label>Database</label>
                        <input type="text" value={pgDb} onChange={(e) => setPgDb(e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label>User</label>
                        <input type="text" value={pgUser} onChange={(e) => setPgUser(e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input type="password" value={pgPass} onChange={(e) => setPgPass(e.target.value)} />
                    </div>
                </div>
            )}

            {error && (
                <div style={{ color: '#ef4444', fontSize: '0.85rem', marginTop: '12px' }}>
                    {error}
                </div>
            )}

            <button
                className="btn-primary"
                style={{ marginTop: '24px', width: '100%' }}
                onClick={handleConnect}
                disabled={isLoading}
            >
                {isLoading ? 'Connecting...' : 'Connect to Database'}
            </button>
        </div>
    )
}

export default ConnectionPanel
