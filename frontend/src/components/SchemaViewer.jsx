function SchemaViewer({ schema }) {
    if (!schema || !schema.tables) return <div>No schema loaded</div>

    return (
        <div className="schema-viewer">
            {schema.tables.map((table) => (
                <div key={table.table_name} className="card" style={{ marginBottom: '24px' }}>
                    <h3 style={{ marginBottom: '16px', color: 'var(--accent-color)' }}>
                        🗂 {table.table_name}
                    </h3>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Column Name</th>
                                    <th>Type</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                {table.columns.map((col) => (
                                    <tr key={col.name}>
                                        <td style={{ fontWeight: '500' }}>{col.name}</td>
                                        <td style={{ fontFamily: 'monospace', color: '#f59e0b' }}>{col.type}</td>
                                        <td>
                                            <input
                                                type="text"
                                                placeholder="Add description..."
                                                style={{
                                                    background: 'transparent',
                                                    border: 'none',
                                                    width: '100%',
                                                    color: 'var(--text-secondary)'
                                                }}
                                            />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            ))}
            {schema.tables.length === 0 && <p>No tables found in this database.</p>}
        </div>
    )
}

export default SchemaViewer
