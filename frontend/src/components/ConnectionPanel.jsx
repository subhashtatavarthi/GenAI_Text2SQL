import { useState, useEffect } from 'react'

function ConnectionPanel({ onConnect, setLlmProvider, currentLlm, setLlmModel, currentModel }) {
    const [dbType, setDbType] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')
    const [isTestSuccessful, setIsTestSuccessful] = useState(false)
    const [connectionData, setConnectionData] = useState(null)
    const [testMessage, setTestMessage] = useState('')

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
    const [sqlitePath, setSqlitePath] = useState('')
    const [pgHost, setPgHost] = useState('')
    const [pgPort, setPgPort] = useState('')
    const [pgDb, setPgDb] = useState('')
    const [pgTable, setPgTable] = useState('')

    // Reset test status when inputs change
    useEffect(() => {
        setIsTestSuccessful(false)
        setConnectionData(null)
        setError('')
        setTestMessage('')
    }, [sqlitePath, pgHost, pgPort, pgDb, pgTable, dbType])

    const handleTestConnection = async () => {
        setIsLoading(true)
        setError('')
        setTestMessage('')

        const payload = {
            type: dbType,
            details: {}
        }

        if (dbType === 'sqlite') {
            payload.details = { file_path: sqlitePath }
        } else {
            payload.details = {
                // user, password handled by backend config
                host: pgHost || undefined,
                port: Number(pgPort) || undefined,
                database: pgDb,
                table_name: pgTable
            }
        }

        try {
            const res = await fetch('/api/v1/get-schema', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })

            if (!res.ok) {
                const errorText = await res.text();
                let errorMsg = 'Failed to connect';
                try {
                    const err = JSON.parse(errorText);
                    errorMsg = err.detail || 'Unknown backend error';
                } catch (e) {
                    errorMsg = errorText || `HTTP Error ${res.status}`;
                }
                throw new Error(errorMsg);
            }

            const data = await res.json()

            // Success! Store data for submit
            setConnectionData({ payload, data })
            setIsTestSuccessful(true)
            setTestMessage('✅ Connection Successful! You can now submit.')

        } catch (e) {
            setError(`Test Connection Failed: ${e.message}`)
            setIsTestSuccessful(false)
        } finally {
            setIsLoading(false)
        }
    }

    const [isOnboarded, setIsOnboarded] = useState(false)
    const [onboardedTables, setOnboardedTables] = useState([])

    const handleSubmit = async () => {
        if (!connectionData || !isTestSuccessful) return;

        let onboardingPayload = {}

        if (dbType === 'sqlite') {
            onboardingPayload = {
                type: 'sqlite',
                file_path: sqlitePath,
                table_name: sqlitePath
            }
        } else {
            // Postgres
            onboardingPayload = {
                type: 'postgres',
                host: pgHost || "localhost",
                port: Number(pgPort) || 5432,
                database: pgDb,
                table_name: pgTable,
                // User/Pass are handled by backend defaults
            }
        }

        try {
            setIsLoading(true)
            const res = await fetch('/api/v1/onboard-table', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(onboardingPayload)
            })

            if (!res.ok) {
                const err = await res.json()
                throw new Error(err.detail || 'Failed to onboard table')
            }

            const data = await res.json()

            // Success
            setIsOnboarded(true)
            setOnboardedTables(prev => [...prev, { ...onboardingPayload, ...data }])
            onConnect(connectionData.payload, connectionData.data) // Keep original parent callback

        } catch (e) {
            setError(`Onboarding Failed: ${e.message}`)
        } finally {
            setIsLoading(false)
        }
    }

    if (isOnboarded) {
        return (
            <div className="connection-panel card" style={{ padding: '32px', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
                <h2 style={{ fontSize: '1.5rem', marginBottom: '24px' }}>✅ Table Onboarded!</h2>
                <div style={{ textAlign: 'left', background: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '8px' }}>
                    <h4 style={{ marginBottom: '12px' }}>Registered Tables</h4>
                    {onboardedTables.map((tbl, idx) => (
                        <div key={idx} style={{ padding: '8px', borderBottom: '1px solid var(--border-color)' }}>
                            <strong>{tbl.table_name}</strong> <span style={{ color: 'var(--text-secondary)' }}>({tbl.database})</span>
                        </div>
                    ))}
                </div>
                <p style={{ marginTop: '24px', color: 'var(--text-secondary)' }}>
                    You can now proceed to query this table. (Feature coming soon)
                </p>
                <button
                    className="btn-secondary"
                    onClick={() => setIsOnboarded(false)}
                    style={{ marginTop: '16px' }}
                >
                    Add Another Table
                </button>
            </div>
        )
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
                        <div className="pg-form" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            {/* Row 1: Host and Port */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                                <div className="form-group">
                                    <label>Host</label>
                                    <input
                                        type="text"
                                        value={pgHost}
                                        onChange={(e) => setPgHost(e.target.value)}
                                        placeholder="e.g. localhost"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Port</label>
                                    <input
                                        type="number"
                                        value={pgPort}
                                        onChange={(e) => setPgPort(e.target.value)}
                                        placeholder="5432"
                                    />
                                </div>
                            </div>

                            {/* Row 2: Database and Table */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                                <div className="form-group">
                                    <label>Database Name</label>
                                    <input
                                        type="text"
                                        value={pgDb}
                                        onChange={(e) => setPgDb(e.target.value)}
                                        placeholder="e.g. sales_db"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Table Name</label>
                                    <input
                                        type="text"
                                        value={pgTable}
                                        onChange={(e) => setPgTable(e.target.value)}
                                        placeholder="e.g. sales_data"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Status Messages */}
                    {error && (
                        <div style={{ color: '#ef4444', fontSize: '0.9rem', marginTop: '24px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            ⚠️ <span>{error}</span>
                        </div>
                    )}

                    {testMessage && (
                        <div style={{ color: '#10b981', fontSize: '0.9rem', marginTop: '24px', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span>{testMessage}</span>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div style={{ display: 'flex', gap: '16px', marginTop: '32px' }}>
                        <button
                            className="btn-secondary"
                            style={{ flex: 1, padding: '16px', fontSize: '1rem', background: 'var(--card-bg)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
                            onClick={handleTestConnection}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Testing...' : 'Test Connection'}
                        </button>

                        <button
                            className="btn-primary"
                            style={{
                                flex: 1,
                                padding: '16px',
                                fontSize: '1rem',
                                opacity: isTestSuccessful ? 1 : 0.5,
                                cursor: isTestSuccessful ? 'pointer' : 'not-allowed'
                            }}
                            onClick={handleSubmit}
                            disabled={!isTestSuccessful || isLoading}
                        >
                            Submit
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}

export default ConnectionPanel
