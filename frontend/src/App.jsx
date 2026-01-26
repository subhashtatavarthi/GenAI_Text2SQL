import { useState } from 'react'
import ConnectionPanel from './components/ConnectionPanel'
import SchemaViewer from './components/SchemaViewer'
import ChatInterface from './components/ChatInterface'

function App() {
  const [dbConfig, setDbConfig] = useState(null)
  const [llmProvider, setLlmProvider] = useState('openai')
  const [llmModel, setLlmModel] = useState('gpt-3.5-turbo')
  const [schema, setSchema] = useState(null)
  const [activeTab, setActiveTab] = useState('onboarding') // onboarding | schema | chat
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

        <nav className="nav-menu">
          <button
            className={`nav-item ${activeTab === 'onboarding' ? 'active' : ''}`}
            onClick={() => setActiveTab('onboarding')}
          >
            🚀 Onboarding
          </button>

          {isConnected && (
            <>
              <button
                className={`nav-item ${activeTab === 'schema' ? 'active' : ''}`}
                onClick={() => setActiveTab('schema')}
              >
                📊 Schema Viewer
              </button>
              <button
                className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`}
                onClick={() => setActiveTab('chat')}
              >
                💬 Chat Interface
              </button>
            </>
          )}
        </nav>

        {isConnected && (
          <div className="status-card" style={{ marginTop: 'auto', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
            <div style={{ color: '#34d399', fontSize: '0.9rem', fontWeight: '500' }}>✅ Connected</div>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{dbConfig.type}</div>
          </div>
        )}
      </div>

      <div className="main-content">
        {activeTab === 'onboarding' && (
          <div className="onboarding-container" style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
            <ConnectionPanel
              onConnect={handleConnect}
              setLlmProvider={setLlmProvider}
              currentLlm={llmProvider}
              setLlmModel={setLlmModel}
              currentModel={llmModel}
            />
          </div>
        )}

        {isConnected && (
          <>
            {activeTab === 'schema' && <SchemaViewer schema={schema} />}
            {activeTab === 'chat' && <ChatInterface llmProvider={llmProvider} llmModel={llmModel} />}
          </>
        )}
      </div>
    </div>
  )
}

export default App
