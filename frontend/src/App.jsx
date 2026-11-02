import React, { useState, useEffect } from 'react';
import {
  Sun,
  Moon,
  Sparkles
} from 'lucide-react';

import LiveInspection from './components/LiveInspection';
import ChatbotView from './components/ChatbotView';
import ModelSpecs from './components/ModelSpecs';
import LandingPage from './components/LandingPage';
import helioBotImg from './assets/helio_bot.jpg';

export default function App() {
  const [activeTab, setActiveTab] = useState('landing'); // 'landing' | 'live' | 'specs' | 'ai-query'
  const [scanContext, setScanContext] = useState(null);
  const [theme, setTheme] = useState(() => localStorage.getItem('helioscan_theme') || 'day');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('helioscan_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'day' ? 'dark' : 'day'));
  };

  const handleOpenChatWithContext = (prediction) => {
    setScanContext(prediction);
    setActiveTab('ai-query');
  };

  return (
    <div className="discord-app-wrapper" data-theme={theme}>
      {/* Classic Broader Blur-Transparent Header */}
      <header className="discord-header">
        <div className="discord-header-inner">
          {/* Left: Brand */}
          <div className="discord-brand" onClick={() => setActiveTab('landing')}>
            <div className="discord-brand-logo">
              <Sun size={22} className="solar-logo-icon" />
            </div>
            <div className="discord-brand-name">
              HelioScan<span className="brand-dot">.</span>AI
            </div>
          </div>

          {/* Center: Minimal Navigation (Home, Live Inspection, Model Benchmark) */}
          <nav className="discord-nav" aria-label="Main Navigation">
            <button
              className={`discord-nav-link ${activeTab === 'landing' ? 'active' : ''}`}
              onClick={() => setActiveTab('landing')}
              id="tab-landing"
            >
              <span>Home</span>
            </button>
            <button
              className={`discord-nav-link ${activeTab === 'live' ? 'active' : ''}`}
              onClick={() => setActiveTab('live')}
              id="tab-live-inspection"
            >
              <span>Live Inspection</span>
            </button>
            <button
              className={`discord-nav-link ${activeTab === 'specs' ? 'active' : ''}`}
              onClick={() => setActiveTab('specs')}
              id="tab-specs"
            >
              <span>Model Evaluation</span>
            </button>
          </nav>

          {/* Right: Theme Toggle & Unique Cartoon Mascot Button */}
          <div className="discord-header-right">
            {/* Day / Night Theme Toggle */}
            <button
              type="button"
              className="theme-toggle-btn"
              onClick={toggleTheme}
              id="btn-theme-toggle"
              title={theme === 'day' ? 'Switch to Black-Golden Night Mode' : 'Switch to Classic Beige Day Mode'}
            >
              {theme === 'day' ? (
                <>
                  <Moon size={15} className="theme-toggle-icon" />
                  <span className="theme-toggle-label">Night</span>
                </>
              ) : (
                <>
                  <Sun size={15} className="theme-toggle-icon golden" />
                  <span className="theme-toggle-label">Day</span>
                </>
              )}
            </button>

            {/* Unique Cartoon UI Button */}
            <button
              type="button"
              className={`cartoon-ai-btn ${activeTab === 'ai-query' ? 'active' : ''}`}
              onClick={() => setActiveTab('ai-query')}
              id="btn-cartoon-ai-copilot"
              title="Launch HelioBot AI Copilot"
            >
              <div className="cartoon-btn-avatar-wrap">
                <img src={helioBotImg} alt="HelioBot" className="cartoon-btn-img" />
              </div>
              <div className="cartoon-btn-text">
                <span className="cartoon-btn-title">Ask HelioBot</span>
                <span className="cartoon-btn-badge">AI COPILOT</span>
              </div>
              <span className="cartoon-btn-bubble">Chat 💬</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="discord-main-container">
        {activeTab === 'landing' && (
          <LandingPage
            onEnterInspection={() => setActiveTab('live')}
            onEnterBenchmark={() => setActiveTab('specs')}
          />
        )}
        {activeTab === 'live' && (
          <LiveInspection
            onOpenChatWithContext={handleOpenChatWithContext}
            onNavigateToBenchmark={() => setActiveTab('specs')}
          />
        )}
        {activeTab === 'specs' && <ModelSpecs />}
        {activeTab === 'ai-query' && (
          <ChatbotView
            scanContext={scanContext}
            onBackToLive={() => setActiveTab('live')}
          />
        )}
      </main>

      {/* Persistent Floating Cartoon Mascot Button (when on other tabs) */}
      {activeTab !== 'ai-query' && (
        <aside
          className="floating-cartoon-bot"
          onClick={() => setActiveTab('ai-query')}
          id="btn-floating-bot"
          title="Click to chat with HelioBot AI Copilot"
        >
          <div className="floating-bot-speech">
            Ask HelioBot! 💬
          </div>
          <div className="floating-bot-bubble">
            <img src={helioBotImg} alt="HelioBot" className="floating-bot-img" />
            <div className="floating-bot-sparkle">
              <Sparkles size={12} />
            </div>
          </div>
        </aside>
      )}

      {/* Minimal Discord-Style Footer */}
      <footer className="discord-footer">
        <div className="discord-footer-inner">
          <div className="footer-left">
            <strong>HelioScan AI</strong> • MobileNetV2 Solar Quality Control Engine
          </div>
          <div className="footer-right">
            <span>Perovskite &amp; Silicon Tandem Inspection</span>
            <span>•</span>
            <span>Metal GPU ~35ms</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
