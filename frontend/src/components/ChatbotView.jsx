import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Sparkles,
  Key,
  Eye,
  EyeOff,
  Check,
  RotateCcw,
  Copy,
  Zap,
  Activity,
  ShieldCheck,
  AlertTriangle,
  Bot,
  User,
  Settings,
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import helioBotImg from '../assets/helio_bot.jpg';

export default function ChatbotView({ scanContext, onBackToLive }) {
  // LLM Config state
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('helioscan_llm_api_key') || '');
  const [provider, setProvider] = useState(() => localStorage.getItem('helioscan_llm_provider') || 'gemini');
  const [selectedModel, setSelectedModel] = useState(() => localStorage.getItem('helioscan_llm_model') || 'auto');
  const [showKey, setShowKey] = useState(false);
  const [keySaved, setKeySaved] = useState(false);
  const [showConfig, setShowConfig] = useState(false);

  // Chat state
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        `### 👋 Hello! I'm HelioBot — Your Photovoltaic AI Specialist\n\n` +
        `I am trained on **perovskite, silicon tandem, and multi-junction solar physics**, as well as the **MobileNetV2 96.0% accuracy** quality inspection model.\n\n` +
        `💡 **LLM Integration:** You can enter your **Google Gemini** or **OpenAI API Key** in the settings bar above to unlock live, customized AI reasoning, or query me using the built-in domain knowledge base!`,
      suggestions: [
        "Why did the current scan pass or fail?",
        "How does Halide Segregation affect open-circuit voltage?",
        "Explain the physical mechanism of layer delamination",
        "How to prevent pinhole shunts during anti-solvent dripping?",
        "Explain the MobileNetV2 architecture in this project"
      ],
      providerUsed: 'built_in',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedIdx, setCopiedIdx] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Insert active scan notification if scanContext is provided
  useEffect(() => {
    if (scanContext && scanContext.displayName) {
      const contextMsg = {
        role: 'system',
        content: `Active Wafer Loaded: **${scanContext.displayName}** (${scanContext.status}) with **${scanContext.confidence}% confidence**. Ask me about the physical failure mechanism or fab remedies!`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, contextMsg]);
    }
  }, [scanContext?.predictedClass]);

  const handleKeyChange = (val) => {
    const trimmed = val.trim();
    setApiKey(val);
    // Smart auto-detection of provider based on key format
    if (trimmed.startsWith('sk-') && provider !== 'openai') {
      setProvider('openai');
    } else if (trimmed.startsWith('AIzaSy') && provider !== 'gemini') {
      setProvider('gemini');
    }
  };

  const handleSaveKey = () => {
    localStorage.setItem('helioscan_llm_api_key', apiKey.trim());
    localStorage.setItem('helioscan_llm_provider', provider);
    localStorage.setItem('helioscan_llm_model', selectedModel);
    setKeySaved(true);
    setTimeout(() => setKeySaved(false), 2500);
  };

  const handleClearKey = () => {
    setApiKey('');
    localStorage.removeItem('helioscan_llm_api_key');
    setKeySaved(false);
  };

  const handleSend = async (queryText = null) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMessage = {
      role: 'user',
      content: textToSend,
      timestamp: currentTime
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!queryText) setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          history: messages.slice(-6).map((m) => ({ role: m.role, content: m.content })),
          scanContext: scanContext || null,
          apiKey: apiKey.trim() || null,
          provider: provider,
          model: selectedModel === 'auto' ? null : selectedModel,
        }),
      });

      if (!res.ok) {
        throw new Error(`Chat API error (${res.status})`);
      }

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.reply,
          suggestions: data.suggestions || [],
          providerUsed: data.providerUsed || (apiKey ? provider : 'built_in'),
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ **Error communicating with AI service**: ${err.message}. Please check your connection or backend server.`,
          suggestions: ["Retry question", "Check system status"],
          providerUsed: 'error',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <div className="discord-chat-layout">
      {/* Cartoon Mascot Hero Header */}
      <div className="discord-panel mascot-hero-bar">
        <div className="mascot-left-group">
          <div className="mascot-avatar-frame">
            <img src={helioBotImg} alt="HelioBot Mascot" className="mascot-img" />
            <div className="mascot-online-dot" />
          </div>
          <div className="mascot-intro-texts">
            <div className="mascot-name-row">
              <h3>HelioBot</h3>
              <span className="bot-pill-badge">BOT</span>
              <span className="copilot-tag">Photovoltaic AI Specialist</span>
            </div>
            <p className="mascot-subline">
              Trained on MobileNetV2 (96.0% Acc), perovskite/tandem degradation physics, and semiconductor fab mitigation.
            </p>
          </div>
        </div>

        <div className="mascot-actions-group">
          <button
            type="button"
            className={`btn-toggle-config ${apiKey ? 'configured' : ''}`}
            onClick={() => setShowConfig(!showConfig)}
            id="btn-toggle-llm-settings"
          >
            <Key size={14} />
            <span>{apiKey ? `${provider.toUpperCase()} API Key Active` : 'Configure LLM API Key'}</span>
            <Settings size={13} style={{ opacity: 0.7 }} />
          </button>
        </div>
      </div>

      {/* Collapsible / Expandable LLM Configuration Bar */}
      {showConfig && (
        <div className="discord-panel llm-config-panel">
          <div className="config-header">
            <div className="config-title">
              <Key size={16} className="accent-amber" />
              <strong>LLM API Configuration</strong>
              <span className="config-hint">Enter your LLM API Key for real-time generative reasoning</span>
            </div>
            <span className="config-status-badge">
              {apiKey ? (
                <span className="status-connected">🟢 Connected to {provider.toUpperCase()}</span>
              ) : (
                <span className="status-offline">🟡 Built-in Domain Knowledge Base</span>
              )}
            </span>
          </div>

          <div className="config-inputs-row">
            <div className="provider-select-group">
              <label>Provider:</label>
              <select
                value={provider}
                onChange={(e) => {
                  setProvider(e.target.value);
                  setSelectedModel('auto');
                }}
                className="discord-select"
                id="select-llm-provider"
              >
                <option value="gemini">Google Gemini</option>
                <option value="openai">OpenAI</option>
              </select>
            </div>

            <div className="model-select-group">
              <label>Model:</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="discord-select"
                id="select-llm-model"
              >
                <option value="auto">Auto-Detect Best Available</option>
                {provider === 'gemini' ? (
                  <>
                    <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                    <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                  </>
                ) : (
                  <>
                    <option value="gpt-4o-mini">GPT-4o Mini (Fast)</option>
                    <option value="gpt-4o">GPT-4o (High Reasoning)</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  </>
                )}
              </select>
            </div>

            <div className="api-key-input-group">
              <label>API Key:</label>
              <div className="input-with-eye">
                <input
                  type={showKey ? 'text' : 'password'}
                  placeholder={provider === 'gemini' ? 'AIzaSy...' : 'sk-...'}
                  value={apiKey}
                  onChange={(e) => handleKeyChange(e.target.value)}
                  className="discord-input"
                  id="input-llm-api-key"
                />
                <button
                  type="button"
                  className="btn-eye"
                  onClick={() => setShowKey(!showKey)}
                  title={showKey ? 'Hide key' : 'Show key'}
                >
                  {showKey ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <div className="key-buttons-group">
              <button
                type="button"
                className="btn-discord-primary"
                onClick={handleSaveKey}
                id="btn-save-api-key"
              >
                {keySaved ? <Check size={14} /> : <Check size={14} />}
                <span>{keySaved ? 'Saved!' : 'Save Key'}</span>
              </button>
              {apiKey && (
                <button
                  type="button"
                  className="btn-discord-secondary"
                  onClick={handleClearKey}
                  id="btn-clear-api-key"
                >
                  <RotateCcw size={13} />
                  <span>Clear</span>
                </button>
              )}
            </div>
          </div>
          <p className="config-note">
            🔒 Your API key is stored locally in your browser’s localStorage. It is transmitted only to call your selected provider.
          </p>
        </div>
      )}

      {/* Active Scan Context Banner */}
      {scanContext && (
        <div className="active-scan-banner">
          <div className="banner-info">
            <Activity size={16} className="text-amber" />
            <span>Active Wafer Context:</span>
            <strong>{scanContext.displayName}</strong>
            <span className={`status-chip ${scanContext.status === 'PASS' ? 'pass' : 'fail'}`}>
              {scanContext.status} ({scanContext.confidence}%)
            </span>
          </div>
          <button
            type="button"
            className="btn-chip-action"
            onClick={() => handleSend("Diagnose the physical cause of this scan result and suggest fab line remedies.")}
          >
            Ask HelioBot to Diagnose This Wafer ➔
          </button>
        </div>
      )}

      {/* Message Stream */}
      <div className="discord-messages-stream" id="messages-stream">
        {messages.map((msg, idx) => {
          if (msg.role === 'system') {
            return (
              <div key={idx} className="discord-system-message">
                <ShieldCheck size={14} className="text-blue" />
                <span>{msg.content}</span>
              </div>
            );
          }

          const isUser = msg.role === 'user';
          return (
            <div key={idx} className={`discord-message-row ${isUser ? 'user-row' : 'bot-row'}`}>
              <div className="discord-avatar">
                {isUser ? (
                  <div className="user-avatar-circle">
                    <User size={18} />
                  </div>
                ) : (
                  <img src={helioBotImg} alt="HelioBot" className="bot-avatar-img" />
                )}
              </div>

              <div className="discord-message-body">
                <div className="discord-message-meta">
                  <span className="author-name">{isUser ? 'Operator' : 'HelioBot'}</span>
                  {!isUser && <span className="bot-tag">BOT</span>}
                  {!isUser && msg.providerUsed && (
                    <span className="provider-tag">
                      {msg.providerUsed === 'gemini'
                        ? 'Gemini LLM'
                        : msg.providerUsed === 'openai'
                        ? 'OpenAI LLM'
                        : 'Physics Engine'}
                    </span>
                  )}
                  <span className="message-timestamp">{msg.timestamp}</span>
                </div>

                <div className="discord-message-text">
                  {msg.content.split('\n').map((line, lIdx) => {
                    if (line.startsWith('### ')) {
                      return <h3 key={lIdx}>{line.replace('### ', '')}</h3>;
                    }
                    if (line.startsWith('#### ')) {
                      return <h4 key={lIdx}>{line.replace('#### ', '')}</h4>;
                    }
                    if (line.startsWith('- **') || line.startsWith('• **')) {
                      return (
                        <div key={lIdx} className="bullet-line">
                          <span className="bullet-dot">•</span>
                          <span>{line.replace(/^[-•]\s*/, '')}</span>
                        </div>
                      );
                    }
                    if (!line.trim()) {
                      return <div key={lIdx} style={{ height: '0.4rem' }} />;
                    }
                    return <p key={lIdx}>{line}</p>;
                  })}
                </div>

                {/* Suggestions Chips */}
                {!isUser && msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="discord-suggestions-row">
                    {msg.suggestions.map((sug, sIdx) => (
                      <button
                        key={sIdx}
                        type="button"
                        className="suggestion-chip"
                        onClick={() => handleSend(sug)}
                      >
                        <Sparkles size={11} />
                        <span>{sug}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {!isUser && (
                <button
                  type="button"
                  className="btn-copy-msg"
                  onClick={() => handleCopy(msg.content, idx)}
                  title="Copy response"
                >
                  {copiedIdx === idx ? <Check size={13} /> : <Copy size={13} />}
                </button>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="discord-message-row bot-row loading">
            <div className="discord-avatar">
              <img src={helioBotImg} alt="HelioBot" className="bot-avatar-img spin-subtle" />
            </div>
            <div className="discord-message-body">
              <div className="discord-message-meta">
                <span className="author-name">HelioBot</span>
                <span className="bot-tag">BOT</span>
              </div>
              <div className="thinking-dots">
                <span />
                <span />
                <span />
                <span className="thinking-text">
                  {apiKey ? `Consulting ${provider.toUpperCase()} LLM...` : 'Analyzing defect physics knowledge...'}
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Discord-style Input Bar */}
      <div className="discord-input-container">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="discord-chat-form"
        >
          <input
            type="text"
            placeholder={
              apiKey
                ? `Ask HelioBot with ${provider.toUpperCase()} (e.g., 'Diagnose this scan', 'Hoke effect', 'Anti-solvent tips')...`
                : "Ask HelioBot (or configure your LLM API Key above)..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="discord-chat-input"
            id="chat-user-input"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="discord-send-btn"
            id="btn-send-chat"
            title="Send query"
          >
            <Send size={16} />
          </button>
        </form>
        <div className="input-footer-hint">
          <span>Press <strong>Enter</strong> to send • Powered by MobileNetV2 (96.0% Acc) &amp; Photovoltaic Domain Intelligence</span>
        </div>
      </div>
    </div>
  );
}
