import React from 'react';
import { Sun, Moon, MessageSquare, Radio, Sparkles, User, LogOut, KeyRound, BarChart3 } from 'lucide-react';
import { useRagulStore } from '../store/useRagulStore';

interface HeaderProps {
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  isSideChatOpen: boolean;
  onToggleSideChat: () => void;
  onOpenLogin: () => void;
  isLeftDiagramOpen?: boolean;
  onToggleLeftDiagram?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  theme,
  onToggleTheme,
  isSideChatOpen,
  onToggleSideChat,
  onOpenLogin,
  isLeftDiagramOpen,
  onToggleLeftDiagram
}) => {
  const { messages, isListening, isSpeaking, currentUser, setCurrentUser, addMessage } = useRagulStore();

  const handleLogout = () => {
    setCurrentUser(null);
    addMessage({
      role: 'assistant',
      content: 'You have logged out from your farm. Please sign in again with your phone number and password to access your farm telemetry.'
    });
  };

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
        {currentUser ? (
          <div className="user-logged-badge" title={`Farm: ${currentUser.farm_name} (${currentUser.farm_code})`}>
            <span className="user-icon-dot" />
            <User size={13} className="text-cyan-400" />
            <span className="user-name-text">{currentUser.full_name}</span>
            <span className="farm-code-tag">{currentUser.farm_code}</span>
            <button
              onClick={handleLogout}
              className="logout-mini-btn"
              title="Logout from this farm"
            >
              <LogOut size={12} />
            </button>
          </div>
        ) : (
          <button onClick={onOpenLogin} className="login-header-btn">
            <KeyRound size={13} />
            <span>Farm Login</span>
          </button>
        )}

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
