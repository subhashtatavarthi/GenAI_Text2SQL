import { useState } from 'react'

function ConnectionPanel({ onConnect, setLlmProvider, currentLlm, setLlmModel, currentModel }) {
    const [dbType, setDbType] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')

    // Model Options
    const modelOptions = {
        openai: [
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
            { id: 'gpt-4o', name: 'GPT-4o' },
            { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
            { id: 'o1-mini', name: 'o1-mini' }
        ],
        gemini: [
            { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash' },
            { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro' }
        ]
    }

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
            const res = await fetch('/api/v1/get-schema', {
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
            onConnect(payload, data)

        } catch (e) {
            setError(e.message)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="connection-panel card" style={{ padding: '32px', maxWidth: '800px', margin: '0 auto' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
                🚀 Onboarding
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
                Connect your database to get started.
            </p>

            {/* Database Selection */}
            <div className="form-group" style={{ marginBottom: '24px' }}>
                <label style={{ marginBottom: '12px', display: 'block', fontSize: '1rem' }}>Select Database Type</label>
                <div className="radio-group" style={{ display: 'flex', flexDirection: 'row', gap: '24px' }}>
                    <div
                        className={`radio-card ${dbType === 'postgres' ? 'selected' : ''}`}
                        onClick={() => setDbType('postgres')}
                        style={{ flexDirection: 'row', padding: '24px', flex: 1, alignItems: 'center', justifyContent: 'flex-start', minHeight: '100px', gap: '16px' }}
                    >
                        <input
                            type="radio"
                            checked={dbType === 'postgres'}
                            readOnly
                            style={{ width: '20px', height: '20px', margin: 0, cursor: 'pointer' }}
                        />
                        <span className="radio-icon" style={{ fontSize: '2rem' }}>🐘</span>
                        <div className="radio-label" style={{ fontSize: '1.1rem', textAlign: 'left' }}>
                            PostgreSQL
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 'normal', marginTop: '4px' }}>Enterprise Relational DB</div>
                        </div>
                    </div>
                    <div
                        className={`radio-card ${dbType === 'sqlite' ? 'selected' : ''}`}
                        onClick={() => setDbType('sqlite')}
                        style={{ flexDirection: 'row', padding: '24px', flex: 1, alignItems: 'center', justifyContent: 'flex-start', minHeight: '100px', gap: '16px' }}
                    >
                        <input
                            type="radio"
                            checked={dbType === 'sqlite'}
                            readOnly
                            style={{ width: '20px', height: '20px', margin: 0, cursor: 'pointer' }}
                        />
                        <span className="radio-icon" style={{ fontSize: '2rem' }}>🗄️</span>
                        <div className="radio-label" style={{ fontSize: '1.1rem', textAlign: 'left' }}>
                            SQLite
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 'normal', marginTop: '4px' }}>Local File Database</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Connection Form */}
            {dbType && (
                <div className="db-details-form" style={{ background: 'rgba(0,0,0,0.2)', padding: '32px', borderRadius: '12px', border: '1px solid var(--border-color)', animation: 'fadeIn 0.3s ease-in-out' }}>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '24px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
                        Connection Details
                    </h3>

                    {dbType === 'sqlite' && (
                        <div className="form-group">
                            <label>Database File Path</label>
                            <input
                                type="text"
                                value={sqlitePath}
                                onChange={(e) => setSqlitePath(e.target.value)}
                                placeholder="e.g., sales.db"
                                style={{ padding: '12px' }}
                            />
                            <small style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
                                Enter the path to your SQLite file (relative to backend root).
                            </small>
                        </div>
                    )}

                    {dbType === 'postgres' && (
                        <div className="pg-form" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                            <div className="form-group">
                                <label>Host</label>
                                <input type="text" value={pgHost} onChange={(e) => setPgHost(e.target.value)} />
                            </div>
                            <div className="form-group">
                                <label>Port</label>
                                <input type="number" value={pgPort} onChange={(e) => setPgPort(e.target.value)} />
                            </div>
                            <div className="form-group" style={{ gridColumn: 'span 2' }}>
                                <label>Database Name</label>
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
                        <div style={{ color: '#ef4444', fontSize: '0.9rem', marginTop: '24px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            ⚠️ <span>{error}</span>
                        </div>
                    )}

                    <button
                        className="btn-primary"
                        style={{ marginTop: '32px', width: '100%', padding: '16px', fontSize: '1rem' }}
                        onClick={handleConnect}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Connecting...' : 'Connect and Continue →'}
                    </button>
                </div>
            )}
        </div>
    )
}

export default ConnectionPanel
