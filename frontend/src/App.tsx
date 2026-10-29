import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { TalkingRagul3D } from './components/TalkingRagul3D';
import { ConversationFeed } from './components/ConversationFeed';
import { FarmTelemetryPanel } from './components/FarmTelemetryPanel';
import { LeftDiagramPanel } from './components/LeftDiagramPanel';
import { useRagulStore, ChatMessageItem } from './store/useRagulStore';
import { audioController } from './services/audioEngine';
import { Send, Mic, MicOff, X, MessageSquare, Activity, BarChart3 } from 'lucide-react';
import { LoginModal } from './components/LoginModal';

export const App: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('ragul_theme') as 'dark' | 'light') || 'dark';
  });
  const [isSideChatOpen, setIsSideChatOpen] = useState(false);
  const [isLeftDiagramOpen, setIsLeftDiagramOpen] = useState(false);
  const [activeDiagramMessage, setActiveDiagramMessage] = useState<ChatMessageItem | null>(null);
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

    const isFarmStatusQuery = (text: string): boolean => {
      if (!text) return false;
      const lower = text.toLowerCase().trim();
      const statusPhrases = [
        'today status', "today's status", 'what is today status', "what's today status",
        'what today status', 'today farm status', 'status today', 'farm status',
        'yesterday status', "yesterday's status", 'what is yesterday status', "what's yesterday status",
        'what yesterday status', 'yesterday farm status', 'status yesterday',
        'today summary', 'yesterday summary', 'what happened today', 'what happened yesterday',
        'what happned', 'what hapned', 'happned', 'hapned', 'happened',
        'stausts', 'stiats', 'stauts', 'current status', 'overall status',
        'today stausts', 'today stiats', 'what is today stausts', 'what is today stiats',
        'yesterday stausts', 'yesterday stiats', 'what is yesterday stausts', 'what is yesterday stiats',
        'farm activity', 'yesterday activity', 'today activity', 'yesterday data', 'today data',
        'இன்றைய பண்ணை நிலவரம்', 'இன்றைய நிலவரம்', 'நேற்றைய பண்ணை நிலவரம்', 'நேற்றைய நிலவரம்', 'பண்ணை நிலவரம்', 'நிலவரம்',
        'आज का स्टेटस', 'कल का स्टेटस', 'आज की स्थिति', 'कल की स्थिति', 'फार्म स्टेटस'
      ];
      if (statusPhrases.some(p => lower.includes(p))) return true;
      if (lower.includes('status') || lower.includes('stausts') || lower.includes('stiats') || lower.includes('stauts') || lower.includes('happ') || lower.includes('activit')) {
        if (lower.includes('today') || lower.includes('yesterday') || lower.includes('yester') || lower.includes('farm') || lower.includes('herd') || lower.length < 25) {
          return true;
        }
      }
      return false;
    };

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

        const newAssistantMsg: ChatMessageItem = {
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: data.response,
          tool_meta: data.tool_meta,
          proof_images: data.proof_images || data.tool_meta?.proof_images || [],
          timestamp: new Date().toISOString()
        };

        addMessage(newAssistantMsg);

        // Automatically activate Left Diagram Panel ONLY when user asks for farm status (today or yesterday)
        const isStatusQuery = isFarmStatusQuery(rawMessage) || Boolean(data.tool_meta?.is_status_query);
        if (isStatusQuery) {
          setIsLeftDiagramOpen(true);
          setActiveDiagramMessage(newAssistantMsg);
        }

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
        console.warn(`[App] Ambient audio notice: ${msg}`);
      },
      onClapWake: () => {
        if (!currentUser) return;
        if (!audioController.isSynthesizing) {
          console.log('[App] Clap detected! Activating listening mode...');
          audioController.startStreaming(sessionId).then(() => {
            setListening(true);
          }).catch((err) => {
            console.warn('[App] Clap activation notice:', err);
          });
        }
      }
    });

    const handleFirstUserInteraction = () => {
      (audioController as any).resumeAudioContext?.();
      window.removeEventListener('click', handleFirstUserInteraction);
      window.removeEventListener('keydown', handleFirstUserInteraction);
    };
    window.addEventListener('click', handleFirstUserInteraction);
    window.addEventListener('keydown', handleFirstUserInteraction);

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
    <div className={`app-container ${isSideChatOpen ? 'drawer-open' : ''} ${isLeftDiagramOpen ? 'left-diagram-open' : ''}`}>
      {/* Top Header with Theme Switcher, Diagrams & Status */}
      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        isSideChatOpen={isSideChatOpen}
        onToggleSideChat={() => setIsSideChatOpen(!isSideChatOpen)}
        onOpenLogin={() => setLoginModalOpen(true)}
        isLeftDiagramOpen={isLeftDiagramOpen}
        onToggleLeftDiagram={() => setIsLeftDiagramOpen(!isLeftDiagramOpen)}
      />

      {/* LEFT-SIDE APACHE ECHARTS DATA VISUALIZATION DRAWER */}
      <LeftDiagramPanel
        isOpen={isLeftDiagramOpen}
        onClose={() => setIsLeftDiagramOpen(false)}
        activeMessage={activeDiagramMessage}
        theme={theme}
        farmId={currentUser?.farm_id}
      />

      {/* Floating Trigger on Left Edge when Diagram Drawer is Closed */}
      {!isLeftDiagramOpen && (
        <button
          onClick={() => setIsLeftDiagramOpen(true)}
          className="floating-left-diagram-trigger"
          title="Open Visual Diagrams & Charts"
        >
          <BarChart3 size={17} className="text-cyan-400" />
          <span>Diagrams & Analytics</span>
        </button>
      )}

      {/* Login Modal for Farm Phone & Password Auth */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setLoginModalOpen(false)}
      />

      {/* Main Workspace Layout */}
      <div className="main-workspace-grid">
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
