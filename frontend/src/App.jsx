import { useState } from 'react'
import ConnectionPanel from './components/ConnectionPanel'
import SchemaViewer from './components/SchemaViewer'
import ChatInterface from './components/ChatInterface'
import TablesManager from './components/TablesManager'

const modelOptions = {
  openai: [
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
    { id: 'gpt-4o', name: 'GPT-4o' },
    { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
    { id: 'o1-mini', name: 'o1-mini' }
  ],
  gemini: [
    { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash' },
    { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro' },
    { id: 'gemini-flash-latest', name: 'Gemini Flash Latest' }
  ]
}

function App() {
  const [dbConfig, setDbConfig] = useState(null)
  const [llmProvider, setLlmProvider] = useState('openai')
  const [llmModel, setLlmModel] = useState('gpt-3.5-turbo')
  const [schema, setSchema] = useState(null)
  const [activeTab, setActiveTab] = useState('onboarding') // onboarding | schema | chat | tables
  const [isConnected, setIsConnected] = useState(false)

  const [chatContext, setChatContext] = useState(null)

  const handleConnect = (config, fetchedSchema) => {
    setDbConfig(config)
    setSchema(fetchedSchema)
    setIsConnected(true)
    setActiveTab('schema')
  }

  const handleStartChat = (table) => {
    setChatContext({ table_name: table.name, ...table })
    setActiveTab('chat')
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

          <button
            className={`nav-item ${activeTab === 'tables' ? 'active' : ''}`}
            onClick={() => setActiveTab('tables')}
          >
            📚 Data Dictionary
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

        {/* Model Settings Selector */}
        <div className="model-settings" style={{ marginTop: isConnected ? '10px' : 'auto', paddingTop: '10px', borderTop: '1px solid var(--border-color)' }}>
          <label style={{ fontSize: '0.8rem', marginBottom: '8px', display: 'block', color: 'var(--text-secondary)' }}>Model Provider</label>
          <select
            value={llmProvider}
            onChange={(e) => {
              const newProvider = e.target.value;
              setLlmProvider(newProvider);
              // Auto-select first model for this provider
              setLlmModel(modelOptions[newProvider][0].id);
            }}
            style={{ width: '100%', marginBottom: '10px', fontSize: '0.85rem' }}
          >
            <option value="openai">OpenAI</option>
            <option value="gemini">Google Gemini</option>
          </select>

          <label style={{ fontSize: '0.8rem', marginBottom: '8px', display: 'block', color: 'var(--text-secondary)' }}>Model</label>
          <select
            value={llmModel}
            onChange={(e) => setLlmModel(e.target.value)}
            style={{ width: '100%', fontSize: '0.85rem' }}
          >
            {modelOptions[llmProvider].map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="main-content">
        {activeTab === 'onboarding' && (
          <div className="onboarding-container" style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
            <ConnectionPanel
              onConnect={handleConnect}
            />
          </div>
        )}

        {activeTab === 'tables' && <TablesManager onStartChat={handleStartChat} />}

        {activeTab === 'schema' && isConnected && <SchemaViewer schema={schema} />}

        {activeTab === 'chat' && (
          <ChatInterface
            llmProvider={llmProvider}
            llmModel={llmModel}
            initialContext={chatContext}
          />
        )}
      </div>
    </div>
  )
}

export default App
