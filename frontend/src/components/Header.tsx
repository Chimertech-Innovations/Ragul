import React from 'react';
import { Sun, Moon, MessageSquare, Radio, Sparkles, BarChart3, Activity } from 'lucide-react';
import { useRagulStore } from '../store/useRagulStore';

interface HeaderProps {
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  isSideChatOpen: boolean;
  onToggleSideChat: () => void;
  isLeftDiagramOpen?: boolean;
  onToggleLeftDiagram?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  theme,
  onToggleTheme,
  isSideChatOpen,
  onToggleSideChat,
  isLeftDiagramOpen,
  onToggleLeftDiagram
}) => {
  const { messages, isListening, isSpeaking } = useRagulStore();

  return (
    <header className="header header-minimal">
      <div className="brand-section">
        <div className="brand-avatar-container">
          <img src="/ragul_transparent.png" alt="Ragul Avatar" className="brand-avatar-img" />
          <span className="brand-online-dot" />
        </div>
        <div>
          <div className="brand-title">
            <span>RAGUL AI</span>
          </div>
          <div className="brand-subtitle">PashuX Smart Vision Assistant</div>
        </div>
      </div>

      <div className="header-status-strip">
        <div className="user-logged-badge" title="RAGUL Dairy AI Farm Supervisor Active">
          <span className="user-icon-dot" />
          <Activity size={13} className="text-emerald-400" />
          <span className="user-name-text">Live Supervisor</span>
          <span className="farm-code-tag">ACTIVE</span>
        </div>

        {isListening && (
          <div className="status-chip hearing-chip">
            <Radio size={12} className="animate-spin text-rose-400" />
            <span>Listening...</span>
          </div>
        )}
        {isSpeaking && (
          <div className="status-chip speaking-chip">
            <Sparkles size={12} className="text-cyan-400" />
            <span>Explaining...</span>
          </div>
        )}
      </div>

      <div className="header-controls">
        {onToggleLeftDiagram && (
          <button
            onClick={onToggleLeftDiagram}
            className={`side-chat-btn ${isLeftDiagramOpen ? 'active' : ''}`}
            title="Toggle Visual Diagrams & Analytics"
          >
            <BarChart3 size={17} />
            <span className="chat-btn-label">Diagrams</span>
          </button>
        )}

        <button
          onClick={onToggleTheme}
          className="theme-toggle-btn"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun size={17} className="text-amber-300" /> : <Moon size={17} className="text-indigo-600" />}
          <span className="theme-text">{theme === 'dark' ? 'Light' : 'Dark'}</span>
        </button>

        <button
          onClick={onToggleSideChat}
          className={`side-chat-btn ${isSideChatOpen ? 'active' : ''}`}
          title="Toggle Chat Panel"
        >
          <MessageSquare size={17} />
          <span className="chat-btn-label">Chat Panel</span>
          <span className="msg-counter">{messages.length}</span>
        </button>
      </div>
    </header>
  );
};
