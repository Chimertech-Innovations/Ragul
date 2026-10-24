import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { TalkingRagul3D } from './components/TalkingRagul3D';
import { ConversationFeed } from './components/ConversationFeed';
import { FarmTelemetryPanel } from './components/FarmTelemetryPanel';
import { useRagulStore } from './store/useRagulStore';
import { audioController } from './services/audioEngine';
import { Send, Mic, MicOff, X, MessageSquare, Activity, Sparkles } from 'lucide-react';

import { LoginModal } from './components/LoginModal';

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
    currentUser,
    isLoginModalOpen,
    setLoginModalOpen,
    isListening,
    setListening,
    isSpeaking,
    setSpeaking,
    vadStatus,
    setVadStatus,
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

  // Prompt login if no user logged in yet
  useEffect(() => {
    if (!currentUser) {
      const timer = setTimeout(() => {
        setLoginModalOpen(true);
      }, 1200);
      return () => clearTimeout(timer);
    }
  }, [currentUser, setLoginModalOpen]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleSendMessageRef = React.useRef<(text?: string) => Promise<void>>(async () => {});
  const activeAbortControllerRef = React.useRef<AbortController | null>(null);
  const lastSentMessageRef = React.useRef<{ text: string; time: number }>({ text: '', time: 0 });

  const handleSendMessage = async (textToSend?: string) => {
    const rawMessage = (textToSend || inputValue).trim();
    if (!rawMessage) return;

    const normalizedMsg = rawMessage.toLowerCase().replace(/[^a-z0-9]/g, '');
    const now = Date.now();
    const lastNormalized = lastSentMessageRef.current.text.toLowerCase().replace(/[^a-z0-9]/g, '');
    const timeSinceLast = now - lastSentMessageRef.current.time;

    // Strict Duplicate Suppression:
    // If the exact same question or a subset/extension was dispatched within the last 5 seconds, ignore duplicate!
    if (
      lastNormalized &&
      (lastNormalized === normalizedMsg || 
       (lastNormalized.length > 5 && normalizedMsg.length > 5 && (lastNormalized.includes(normalizedMsg) || normalizedMsg.includes(lastNormalized)))) &&
      timeSinceLast < 5000
    ) {
      console.log('[App] Suppressed duplicate question dispatch:', rawMessage);
      if (!textToSend) setInputValue('');
      return;
    }

    lastSentMessageRef.current = { text: rawMessage, time: now };

    // MANDATORY AUTHENTICATION CHECK: Only logged-in users can access the chatbot!
    if (!currentUser) {
      console.log('[App] Unauthenticated user attempt. Prompting login...');
      setLoginModalOpen(true);
      const isTamil = /[\u0B80-\u0BFF]/.test(rawMessage);
      const isHindi = /[\u0900-\u097F]/.test(rawMessage);
      const loginPromptText = isTamil
        ? "வணக்கம் ஐயா! ரகுல் ஏஐ (RAGUL AI) உங்கள் பண்ணை உதவியாளரை அணுக, தயவுசெய்து உங்கள் பதிவு செய்யப்பட்ட தொலைபேசி எண் மற்றும் கடவுச்சொல் மூலம் உள்நுழையவும் (Login)."
        : isHindi
        ? "नमस्ते सर! RAGUL AI और अपने फार्म डेटा को एक्सेस करने के लिए, कृपया अपने पंजीकृत फोन नंबर और पासवर्ड से लॉगिन (Login) करें।"
        : "Hello Sir! You are currently not logged in. Please log in with your registered phone number and password to access RAGUL AI, your live farm cameras, and cattle records.";

      audioController.stopSpeaking();
      setSpeaking(false);
      triggerInterruption();

      addMessage({ role: 'user', content: rawMessage });
      addMessage({
        role: 'assistant',
        content: loginPromptText,
        tool_meta: { requires_login: true }
      });
      if (!textToSend) setInputValue('');
      setSpeaking(true);
      audioController.speakText(loginPromptText, 'en-US');
      setTimeout(() => setSpeaking(false), 4500);
      return;
    }

    // Instant Barge-In / Interruption:
    // When user speaks a new question, cancel previous speech and abort previous backend request!
    if (activeAbortControllerRef.current) {
      console.log('[App] Aborting previous in-flight request for new question:', rawMessage);
      activeAbortControllerRef.current.abort();
      activeAbortControllerRef.current = null;
    }

    audioController.stopSpeaking();
    setSpeaking(false);
    triggerInterruption();

    addMessage({ role: 'user', content: rawMessage });
    if (!textToSend) setInputValue('');
    setProcessing(true);

    const controller = new AbortController();
    activeAbortControllerRef.current = controller;
    const timeoutId = setTimeout(() => controller.abort(), 25000);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          message: rawMessage,
          language: 'auto',
          session_id: sessionId,
          farm_id: currentUser?.farm_id || null
        })
      });
      clearTimeout(timeoutId);

      // If aborted by a subsequent question, drop quietly
      if (controller.signal.aborted) return;

      if (response.ok) {
        const data = await response.json();
        if (controller.signal.aborted) return;

        setProcessing(false);
        if (data.session_id && data.session_id !== sessionId) {
          setSessionId(data.session_id);
        }

        if (data.tool_meta?.requires_login) {
          setLoginModalOpen(true);
        }

        addMessage({
          role: 'assistant',
          content: data.response,
          tool_meta: data.tool_meta,
          proof_images: data.proof_images || data.tool_meta?.proof_images || []
        });

        // Trigger Talking Animation & TTS Audio
        setSpeaking(true);
        audioController.speakText(data.response, 'en-US');
      } else {
        setProcessing(false);
        addMessage({
          role: 'assistant',
          content: 'Error communicating with farm backend. Please check server status.'
        });
      }
    } catch (e: any) {
      clearTimeout(timeoutId);
      if (controller.signal.aborted) {
        console.log('[App] In-flight request successfully cancelled for second question.');
        return;
      }
      setProcessing(false);
      console.error('Chat error:', e);
      const isTimeout = e?.name === 'AbortError';
      addMessage({
        role: 'assistant',
        content: isTimeout
          ? 'Sir, response took longer than expected (>25 seconds). The AI model or farm database is taking longer to respond. Please try again or ask your question directly.'
          : 'Backend offline. Please ensure the FastAPI server is active on port 8000.'
      });
    } finally {
      if (activeAbortControllerRef.current === controller) {
        activeAbortControllerRef.current = null;
      }
    }
  };

  handleSendMessageRef.current = handleSendMessage;

  useEffect(() => {
    audioController.setCallbacks({
      onInterruption: () => {
        triggerInterruption();
        setSpeaking(false);
        if (activeAbortControllerRef.current) {
          activeAbortControllerRef.current.abort();
          activeAbortControllerRef.current = null;
        }
      },
      onTranscript: (text, lang) => {
        if (text && text.trim()) {
          handleSendMessageRef.current(text.trim());
        }
      },
      onAssistantResponse: (text, toolMeta) => {
        setProcessing(false);
        if (toolMeta?.requires_login) {
          setLoginModalOpen(true);
        }
        addMessage({
          role: 'assistant',
          content: text,
          tool_meta: toolMeta,
          proof_images: toolMeta?.proof_images || []
        });
      },
      onSilenceEnd: () => {
        console.log('[App] User speech query received. Querying backend while keeping microphone continuously armed for hands-free dialogue...');
        // CRITICAL: Do NOT setListening(false)! Keep isListening true for continuous duplex dialogue!
      },
      onSpeechEnd: () => {
        console.log('[App] Assistant finished speaking. Keeping microphone listening for Sir...');
        setSpeaking(false);
        setListening(true);
        audioController.startStreaming(sessionId).then(() => {
          setListening(true);
        }).catch((err) => {
          console.warn('[App] Auto mic keep-alive notice:', err);
        });
      },
      onNoiseAlert: (msg) => {
        // Log to console rather than polluting user's chat feed
        console.warn(`[App] Ambient audio notice: ${msg}`);
      },
      onClapWake: () => {
        if (!currentUser) return; // Do not wake mic if not logged in
        if (!audioController.isSynthesizing) {
          console.log('[App] Clap detected! Activating listening mode...');
          audioController.startStreaming(sessionId).then(() => {
            setListening(true);
          }).catch((err) => {
            console.warn('[App] Clap mic wake notice:', err);
          });
        }
      },
      onVadStatus: (status) => {
        setVadStatus(status);
      }
    });

    return () => {
      audioController.stopStreaming();
    };
  }, [sessionId, triggerInterruption, setProcessing, setListening, setSpeaking, setVadStatus, currentUser]);

  // Hands-free continuous duplex mode: Auto-arm mic on first user interaction so user doesn't need to manually click
  useEffect(() => {
    const handleFirstUserInteraction = () => {
      if (!currentUser) return; // Do not auto-arm mic for unauthenticated users!
      if (!audioController.isListening && !isListening) {
        console.log('[App] First user interaction detected. Auto-arming hands-free microphone...');
        audioController.startStreaming(sessionId).then(() => {
          setListening(true);
        }).catch((err) => {
          console.log('[App] Mic waiting for explicit user gesture:', err);
        });
      }
    };

    window.addEventListener('click', handleFirstUserInteraction, { once: true });
    window.addEventListener('keydown', handleFirstUserInteraction, { once: true });

    return () => {
      window.removeEventListener('click', handleFirstUserInteraction);
      window.removeEventListener('keydown', handleFirstUserInteraction);
    };
  }, [sessionId, isListening, setListening, currentUser]);

  const handleToggleMic = async () => {
    if (!currentUser) {
      setLoginModalOpen(true);
      const loginPromptText = "Sir, please log in with your registered phone number and password to use voice conversation and access your farm chatbot.";
      addMessage({
        role: 'assistant',
        content: loginPromptText,
        tool_meta: { requires_login: true }
      });
      setSpeaking(true);
      audioController.speakText(loginPromptText, 'en-US');
      setTimeout(() => setSpeaking(false), 4500);
      return;
    }

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
        onOpenLogin={() => setLoginModalOpen(true)}
      />

      {/* Login Modal for Farm Phone & Password Auth */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setLoginModalOpen(false)}
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
