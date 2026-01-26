import { useState } from 'react'
import ConnectionPanel from './components/ConnectionPanel'
import SchemaViewer from './components/SchemaViewer'
import ChatInterface from './components/ChatInterface'

function App() {
  const [dbConfig, setDbConfig] = useState(null)
  const [llmProvider, setLlmProvider] = useState('openai')
  const [schema, setSchema] = useState(null)
  const [activeTab, setActiveTab] = useState('schema') // schema | chat
  const [isConnected, setIsConnected] = useState(false)

  const handleConnect = (config, fetchedSchema) => {
    setDbConfig(config)
    setSchema(fetchedSchema)
    setIsConnected(true)
    setActiveTab('schema')
  }

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="brand">GenAI SQL Agent</div>
        <ConnectionPanel
          onConnect={handleConnect}
          setLlmProvider={setLlmProvider}
          currentLlm={llmProvider}
        />

        {isConnected && (
          <div className="status-card" style={{ marginTop: 'auto', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
            <div style={{ color: '#34d399', fontSize: '0.9rem', fontWeight: '500' }}>✅ Connected</div>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{dbConfig.type}</div>
          </div>
        )}
      </div>

      <div className="main-content">
        {!isConnected ? (
          <div className="card" style={{ textAlign: 'center', padding: '64px' }}>
            <h2>Welcome to Text-to-SQL</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '16px' }}>
              Connect to a database using the sidebar to verify schema and start chatting.
            </p>
          </div>
        ) : (
          <>
            <div className="tabs">
              <button
                className={`tab ${activeTab === 'schema' ? 'active' : ''}`}
                onClick={() => setActiveTab('schema')}
              >
                Schema Viewer
              </button>
              <button
                className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
                onClick={() => setActiveTab('chat')}
              >
                Chat Interface
              </button>
            </div>

            <div className="content-area">
              {activeTab === 'schema' && <SchemaViewer schema={schema} />}
              {activeTab === 'chat' && <ChatInterface llmProvider={llmProvider} />}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default App
