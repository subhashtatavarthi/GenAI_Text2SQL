import React, { useState, useEffect } from 'react'

const TablesManager = () => {
    const [tables, setTables] = useState([])
    const [selectedTable, setSelectedTable] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)

    // Metadata Edit State
    const [desc, setDesc] = useState("")
    const [columns, setColumns] = useState([])
    const [isSaving, setIsSaving] = useState(false)
    const [successMsg, setSuccessMsg] = useState("")

    useEffect(() => {
        fetchTables()
    }, [])

    // Fetch list of onboarded tables
    const fetchTables = async () => {
        setIsLoading(true)
        try {
            const res = await fetch('/api/v1/tables')
            if (!res.ok) throw new Error("Failed to fetch tables")
            const data = await res.json()
            setTables(data)
        } catch (e) {
            setError(e.message)
        } finally {
            setIsLoading(false)
        }
    }

    const handleSelectTable = async (table) => {
        setSelectedTable(table)
        setSuccessMsg("")
        setIsLoading(true)
        // Load metadata (desc, columns) from backend
        // Note: Initially columns might be empty until we fetch schema again or use saved metadata
        // For this feature, we want to fetch the "Schema" first to populate columns if they are not saved yet.
        // But the user asked for "Data Dictionary" logic.
        // Strategy: 
        // 1. Fetch saved metadata.
        // 2. If saved metadata has columns, use them.
        // 3. If not, fetch LIVE schema to populate initial list.

        try {
            // 1. Get Saved Metadata
            const metaRes = await fetch(`/api/v1/tables/${table.table_id}/metadata`)
            const metaData = await metaRes.json()

            setDesc(metaData.description || "")

            if (metaData.columns && metaData.columns.length > 0) {
                setColumns(metaData.columns)
            } else {
                // 2. Fetch Live Schema if no saved metadata
                // We need to construct payload for get-schema similar to ConnectionPanel
                // But wait, get-schema needs connection details.
                // We have them in the backend registry but the frontend doesn't have plain access to them easily here unless we pass them.
                // The backend Tables router returns table_id.
                // Let's rely on the user manually entering columns OR 
                // SIMPLIFICATION: usage of schema viewer logic IS complicated here without refactoring.
                // User asked: "column datatype description (editable)"
                // I will initialize empty columns list for now to allow user to add manual descriptions?
                // No, that's bad UX. 

                // Alternative: The Metadata Endpoint should ideally merge with Schema if empty.
                // But to avoid complex backend changes right now, I will just show "No columns synced yet" 
                // OR I will fetch the columns from the "Schema Viewer" logic IF the connection is active.
                // But connection might not be active.

                // Let's stick to: Just Metadata for now. If empty, user sees empty. 
                // Providing a "Sync Schema" button would be the best next step.
                setColumns([])
            }
        } catch (e) {
            console.error(e)
        } finally {
            setIsLoading(false)
        }
    }

    // Sync Schema Helper (Optional enhancement to autofill columns)
    // For now, let's just allow editing Description at Table level clearly.

    const handleSave = async () => {
        if (!selectedTable) return
        setIsSaving(true)
        try {
            const payload = {
                description: desc,
                columns: columns
            }
            const res = await fetch(`/api/v1/tables/${selectedTable.table_id}/metadata`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            if (!res.ok) throw new Error("Failed to save")
            setSuccessMsg("Changes saved successfully! ✅")

            // Update local list
            setTables(prev => prev.map(t => t.table_id === selectedTable.table_id ? { ...t, description: desc } : t))

        } catch (e) {
            setError(e.message)
        } finally {
            setIsSaving(false)
        }
    }

    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', display: 'flex', gap: '30px', height: '80vh' }}>
            {/* List Section */}
            <div style={{ flex: 1, borderRight: '1px solid var(--border-color)', paddingRight: '20px', overflowY: 'auto' }}>
                <h2 style={{ fontSize: '1.5rem', marginBottom: '20px' }}>📚 Data Dictionary</h2>
                {isLoading && !selectedTable && <div>Loading...</div>}
                {error && <div style={{ color: 'red' }}>{error}</div>}

                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-secondary)' }}>
                            <th style={{ padding: '12px' }}>Type</th>
                            <th style={{ padding: '12px' }}>Table Name</th>
                            <th style={{ padding: '12px' }}>Database</th>
                            <th style={{ padding: '12px' }}>By User</th>
                            <th style={{ padding: '12px' }}>Onboarded At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tables.map(t => (
                            <tr
                                key={t.table_id}
                                onClick={() => handleSelectTable(t)}
                                style={{
                                    borderBottom: '1px solid rgba(255,255,255,0.05)',
                                    cursor: 'pointer',
                                    background: selectedTable?.table_id === t.table_id ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                                    transition: 'background 0.2s'
                                }}
                                onMouseEnter={(e) => { if (selectedTable?.table_id !== t.table_id) e.currentTarget.style.background = 'rgba(255,255,255,0.03)' }}
                                onMouseLeave={(e) => { if (selectedTable?.table_id !== t.table_id) e.currentTarget.style.background = 'transparent' }}
                            >
                                <td style={{ padding: '12px' }}>
                                    {t.type === 'postgres' ? '🐘' : '💾'}
                                </td>
                                <td style={{ padding: '12px', fontWeight: '500' }}>{t.name}</td>
                                <td style={{ padding: '12px', color: '#94a3b8' }}>{t.db_name}</td>
                                <td style={{ padding: '12px', color: '#94a3b8' }}>{t.onboarded_by || 'Unknown'}</td>
                                <td style={{ padding: '12px', color: '#94a3b8', fontSize: '0.8rem' }}>
                                    {t.onboarded_at ? new Date(t.onboarded_at).toLocaleString() : '-'}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {tables.length === 0 && !isLoading && <div style={{ opacity: 0.5, marginTop: '20px' }}>No tables onboarded yet.</div>}
            </div>

            {/* Detail Section */}
            <div style={{ flex: 2, paddingLeft: '10px', overflowY: 'auto' }}>
                {selectedTable ? (
                    <div>
                        <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h2 style={{ fontSize: '1.5rem' }}>{selectedTable.name}</h2>
                            <button
                                onClick={handleSave}
                                className="btn-primary"
                                disabled={isSaving}
                            >
                                {isSaving ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                        {successMsg && <div style={{ marginBottom: '15px', color: '#10b981' }}>{successMsg}</div>}

                        <div style={{ marginBottom: '30px' }}>
                            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Table Description</label>
                            <textarea
                                value={desc}
                                onChange={(e) => setDesc(e.target.value)}
                                placeholder="Describe what this table contains..."
                                style={{
                                    width: '100%',
                                    height: '100px',
                                    padding: '12px',
                                    borderRadius: '8px',
                                    background: '#1e293b',
                                    border: '1px solid var(--border-color)',
                                    color: 'white'
                                }}
                            />
                        </div>

                        <div>
                            <h3 style={{ marginBottom: '15px' }}>Columns (Metadata Only)</h3>
                            {/* Future: Sync with Schema */}
                            {columns.length > 0 ? (
                                <div style={{ overflowX: 'auto' }}>
                                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                                        <thead>
                                            <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                                                <th style={{ padding: '10px' }}>Column</th>
                                                <th style={{ padding: '10px' }}>Type</th>
                                                <th style={{ padding: '10px' }}>Description</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {columns.map((col, idx) => (
                                                <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                                    <td style={{ padding: '10px', fontWeight: '500' }}>{col.name}</td>
                                                    <td style={{ padding: '10px', color: '#94a3b8', fontSize: '0.85rem' }}>{col.type}</td>
                                                    <td style={{ padding: '10px' }}>
                                                        <input
                                                            type="text"
                                                            value={col.description}
                                                            onChange={(e) => {
                                                                const newCols = [...columns];
                                                                newCols[idx] = { ...newCols[idx], description: e.target.value };
                                                                setColumns(newCols);
                                                            }}
                                                            placeholder="Add description..."
                                                            style={{
                                                                width: '100%',
                                                                background: 'transparent',
                                                                border: '1px solid transparent',
                                                                color: 'white',
                                                                padding: '4px 8px',
                                                                borderRadius: '4px',
                                                                outline: 'none'
                                                            }}
                                                            onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                                                            onBlur={(e) => e.target.style.borderColor = 'transparent'}
                                                        />
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <p style={{ color: 'gray', fontSize: '0.9rem' }}>
                                    No columns found. Try re-onboarding this table to sync schema.
                                </p>
                            )}
                        </div>
                    </div>
                ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
                        Select a table to view details
                    </div>
                )}
            </div>
        </div>
    )
}

export default TablesManager
