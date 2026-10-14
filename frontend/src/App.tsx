import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { TalkingRagul3D } from './components/TalkingRagul3D';
import { ConversationFeed } from './components/ConversationFeed';
import { FarmTelemetryPanel } from './components/FarmTelemetryPanel';
import { useRagulStore } from './store/useRagulStore';
import { audioController } from './services/audioEngine';
import { Send, Mic, MicOff, X, MessageSquare, Activity, Sparkles } from 'lucide-react';

export const App: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('ragul_theme') as 'dark' | 'light') || 'dark';
  });
  const [isSideChatOpen, setIsSideChatOpen] = useState(false);
  const [activeSideTab, setActiveSideTab] = useState<'chat' | 'telemetry'>('chat');

  const {
    sessionId,
    setSessionId,
    isListening,
    setListening,
    isSpeaking,
    setSpeaking,
    isProcessing,
    setProcessing,
    addMessage,
    triggerInterruption,
    messages
  } = useRagulStore();

  // Apply Theme to Document root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('ragul_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleSendMessageRef = React.useRef<(text?: string) => Promise<void>>(async () => {});

  const handleSendMessage = async (textToSend?: string) => {
    const messageText = (textToSend || inputValue).trim();
    if (!messageText) return;

    addMessage({ role: 'user', content: messageText });
    if (!textToSend) setInputValue('');
    setProcessing(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          language: 'auto',
          session_id: sessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        setProcessing(false);
        if (data.session_id && data.session_id !== sessionId) {
          setSessionId(data.session_id);
        }

        addMessage({
          role: 'assistant',
          content: data.response,
          tool_meta: data.tool_meta
        });

        // Trigger Talking Animation & TTS Audio
        setSpeaking(true);
        audioController.speakText(data.response, 'en-US');
        const estimatedDurationMs = Math.max(3000, data.response.length * 65);
        setTimeout(() => setSpeaking(false), estimatedDurationMs);
      } else {
        setProcessing(false);
        addMessage({
          role: 'assistant',
          content: 'Error communicating with farm backend. Please check server status.'
        });
      }
    } catch (e) {
      setProcessing(false);
      console.error('Chat error:', e);
      addMessage({
        role: 'assistant',
        content: 'Backend offline. Please ensure the FastAPI server is active on port 8000.'
      });
    }
  };

  handleSendMessageRef.current = handleSendMessage;

  useEffect(() => {
    audioController.setCallbacks({
      onInterruption: () => {
        triggerInterruption();
      },
      onTranscript: (text, lang) => {
        if (text && text.trim()) {
          handleSendMessageRef.current(text.trim());
        }
      },
      onAssistantResponse: (text, toolMeta) => {
        setProcessing(false);
        addMessage({ role: 'assistant', content: text, tool_meta: toolMeta });
      },
      onSilenceEnd: () => {
        console.log('[App] User silent. Turning mic off and querying backend...');
        setListening(false);
      },
      onSpeechEnd: () => {
        console.log('[App] Assistant finished speaking. Auto re-arming microphone...');
        setSpeaking(false);
        audioController.startStreaming(sessionId).then(() => {
          setListening(true);
        }).catch((err) => {
          console.warn('[App] Auto mic re-arm notice:', err);
        });
      },
      onNoiseAlert: (msg) => {
        addMessage({
          role: 'system',
          content: `⚠️ ${msg}`
        });
      },
      onClapWake: () => {
        if (!audioController.isSynthesizing) {
          console.log('[App] Clap detected! Activating listening mode...');
          audioController.startStreaming(sessionId).then(() => {
            setListening(true);
          }).catch((err) => {
            console.warn('[App] Clap mic wake notice:', err);
          });
        }
      }
    });

    return () => {
      audioController.stopStreaming();
    };
  }, [sessionId, triggerInterruption, setProcessing, setListening, setSpeaking]);

  const handleToggleMic = async () => {
    if (isListening) {
      audioController.stopStreaming();
      setListening(false);
    } else {
      try {
        await audioController.startStreaming(sessionId);
        setListening(true);
      } catch (e) {
        alert('Could not access microphone. Please grant mic permissions.');
      }
    }
  };

  return (
    <div className={`app-container ${isSideChatOpen ? 'drawer-open' : ''}`}>
      {/* Top Header with Theme Switcher & Status */}
      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        isSideChatOpen={isSideChatOpen}
        onToggleSideChat={() => setIsSideChatOpen(!isSideChatOpen)}
      />

      {/* Main Workspace Layout */}
      <div className="main-workspace-grid">
        {/* CENTER HERO STAGE: 3D Talking Ragul */}
        <main className="hero-stage-panel">
          <TalkingRagul3D
            onToggleMic={handleToggleMic}
            onSendQuery={(query) => {
              handleSendMessage(query);
              setIsSideChatOpen(true);
            }}
          />

          {/* Quick Chat Input Bar on Main Stage */}
          <div className="stage-quick-input-bar">
            <input
              type="text"
              className="chat-input"
              placeholder="Ask Ragul anything in English, தமிழ், or Tanglish..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <button
              className={`btn-icon ${isListening ? 'mic-active' : ''}`}
              onClick={handleToggleMic}
              title={isListening ? 'Stop Listening' : 'Speak to Ragul'}
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
            <button
              className="btn-icon"
              onClick={() => {
                handleSendMessage();
                setIsSideChatOpen(true);
              }}
              disabled={!inputValue.trim() || isProcessing}
              title="Send Inquiry"
            >
              <Send size={16} />
            </button>
          </div>
        </main>

        {/* SLEEK SIDE CHAT & TELEMETRY PANEL (Docked or Floating on Mobile) */}
        <aside className={`side-chat-drawer ${isSideChatOpen ? 'open' : 'closed'}`}>
          <div className="drawer-header">
            <div className="drawer-tabs">
              <button
                className={`drawer-tab-btn ${activeSideTab === 'chat' ? 'active' : ''}`}
                onClick={() => setActiveSideTab('chat')}
              >
                <MessageSquare size={14} />
                <span>Chat History ({messages.length})</span>
              </button>
              <button
                className={`drawer-tab-btn ${activeSideTab === 'telemetry' ? 'active' : ''}`}
                onClick={() => setActiveSideTab('telemetry')}
              >
                <Activity size={14} />
                <span>Farm Telemetry</span>
              </button>
            </div>
            <button
              onClick={() => setIsSideChatOpen(false)}
              className="close-drawer-btn"
              title="Hide Side Panel"
            >
              <X size={18} />
            </button>
          </div>

          <div className="drawer-body">
            {activeSideTab === 'chat' ? (
              <div className="drawer-feed-container">
                <ConversationFeed />

                {/* Input in side drawer */}
                <div className="drawer-input-bar">
                  <input
                    type="text"
                    className="chat-input"
                    placeholder="Type follow-up query..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  />
                  <button
                    className="btn-icon"
                    onClick={() => handleSendMessage()}
                    disabled={!inputValue.trim() || isProcessing}
                  >
                    <Send size={16} />
                  </button>
                </div>
              </div>
            ) : (
              <div className="drawer-telemetry-container">
                <FarmTelemetryPanel />
              </div>
            )}
          </div>
        </aside>
      </div>

      {/* Floating Action Button to View Chat on Small Screens */}
      {!isSideChatOpen && (
        <button
          onClick={() => setIsSideChatOpen(true)}
          className="floating-chat-trigger"
          title="Open Dialogue History"
        >
          <MessageSquare size={20} />
          <span>View Chat History ({messages.length})</span>
        </button>
      )}
    </div>
  );
};
