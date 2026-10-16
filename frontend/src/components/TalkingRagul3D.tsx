import React, { useState, useEffect } from 'react';
import { 
  Mic, 
  MicOff,
  Volume2, 
  Sparkles, 
  AlertTriangle, 
  HeartPulse, 
  Wheat, 
  CheckCircle2, 
  Ear,
  Activity,
  Milk,
  Radio,
  HelpCircle,
  Clock,
  Users
} from 'lucide-react';
import { useRagulStore } from '../store/useRagulStore';

interface TalkingRagul3DProps {
  onToggleMic: () => void;
  onSendQuery?: (query: string) => void;
}

export const TalkingRagul3D: React.FC<TalkingRagul3DProps> = ({ onToggleMic, onSendQuery }) => {
  const { isListening, isSpeaking, isProcessing, interrupted, messages } = useRagulStore();
  const [isWakingUp, setIsWakingUp] = useState(false);
  const [isPoked, setIsPoked] = useState(false);

  // Latest assistant message for dynamic emotion & speech bubble
  const lastAssistantMsg = [...messages].reverse().find((m) => m.role === 'assistant')?.content;

  // Determine Dynamic Action & Mood from AI Response
  const getActionState = (): 'alert' | 'estrus' | 'nutrition' | 'greeting' | 'speaking' | 'listening' | 'thinking' | 'idle' => {
    if (isListening) return 'listening';
    if (isProcessing) return 'thinking';
    if (!isSpeaking || !lastAssistantMsg) return 'idle';
    
    const text = lastAssistantMsg.toLowerCase();

    // Priority 1: Self-Introduction & Greetings
    if (
      text.includes('hello sir') ||
      text.includes('i am ragul') ||
      text.includes('how can i assist') ||
      text.includes('welcome') ||
      text.includes('வணக்கம்') ||
      text.includes('dairy farm ai assistant')
    ) {
      return 'greeting';
    }

    // Priority 2: Health / Mastitis Alerts
    if (
      (text.includes('mastitis') && (text.includes('high') || text.includes('treatment') || text.includes('cmt') || text.includes('quarter') || text.includes('swollen') || text.includes('swelling') || text.includes('infusion') || text.includes('deficit'))) ||
      text.includes('fever') ||
      text.includes('bloat') ||
      text.includes('severe') ||
      text.includes('clinical alert') ||
      text.includes('மடிநோய்')
    ) {
      return 'alert';
    }

    // Priority 3: Estrus & Breeding
    if (
      text.includes('standing heat') ||
      text.includes('in heat') ||
      text.includes('estrus') ||
      text.includes('insemination') ||
      text.includes('breeding window') ||
      text.includes('சினைப்பருவம்')
    ) {
      return 'estrus';
    }

    // Priority 4: Feeding & Nutrition
    if (
      text.includes('feeding schedule') ||
      text.includes('green fodder') ||
      text.includes('feed ration') ||
      text.includes('concentrate') ||
      text.includes('தீவனம்')
    ) {
      return 'nutrition';
    }

    return 'speaking';
  };

  const actionState = getActionState();

  // Trigger 3D Wake Up Animation when greeting detected
  useEffect(() => {
    const lastMsg = messages[messages.length - 1];
    if (lastMsg && lastMsg.role === 'user') {
      const lower = lastMsg.content.toLowerCase();
      if (
        lower.includes('hey ragul') ||
        lower.includes('hi ragul') ||
        lower.includes('hello ragul') ||
        lower.includes('வணக்கம்') ||
        lower.includes('wake up')
      ) {
        setIsWakingUp(true);
        const timer = setTimeout(() => setIsWakingUp(false), 2500);
        return () => clearTimeout(timer);
      }
    }
  }, [messages]);

  const handleCharacterClick = () => {
    setIsPoked(true);
    setTimeout(() => setIsPoked(false), 800);
    onToggleMic();
  };

  const quickQueries = [
    { label: '👥 Workers Present', query: 'How many workers came today?' },
    { label: '🥛 Daily Milk Status', query: 'What is today milk yield and highest cow?' },
    { label: '🩺 Mastitis & Health', query: 'Is there any cow with mastitis risk or sick?' },
    { label: '🌾 Feed Timing', query: 'What time is the evening feeding and milking?' },
  ];

  return (
    <div className={`talking-ragul-stage stage-${actionState}`}>
      {/* 3D Holographic Stage Spotlight & Floor Base */}
      <div
        className={`hologram-beam ${
          actionState === 'alert'
            ? 'beam-alert'
            : actionState === 'estrus'
            ? 'beam-estrus'
            : actionState === 'nutrition'
            ? 'beam-nutrition'
            : isSpeaking
            ? 'beam-speaking'
            : isListening
            ? 'beam-listening'
            : isProcessing
            ? 'beam-thinking'
            : isWakingUp
            ? 'beam-wakeup'
            : ''
        }`}
      />
      <div
        className={`podium-base ${
          actionState === 'alert'
            ? 'podium-alert'
            : actionState === 'estrus'
            ? 'podium-estrus'
            : actionState === 'nutrition'
            ? 'podium-nutrition'
            : isSpeaking
            ? 'podium-speaking'
            : isListening
            ? 'podium-listening'
            : isProcessing
            ? 'podium-thinking'
            : isWakingUp
            ? 'podium-wakeup'
            : ''
        }`}
      />

      {/* Floating Speech Bubble when Ragul explains / speaks */}
      {isSpeaking && lastAssistantMsg && (
        <div className={`tom-speech-bubble bubble-${actionState}`}>
          <div className="bubble-header">
            {actionState === 'alert' ? (
              <>
                <AlertTriangle size={15} className="bubble-icon-pulse alert-icon" />
                <span className="text-rose-400 font-bold">HEALTH ALERT EXPLANATION</span>
              </>
            ) : actionState === 'estrus' ? (
              <>
                <HeartPulse size={15} className="bubble-icon-pulse estrus-icon" />
                <span className="text-emerald-400 font-bold">BREEDING HEAT ADVISORY</span>
              </>
            ) : actionState === 'nutrition' ? (
              <>
                <Wheat size={15} className="bubble-icon-pulse nutrition-icon" />
                <span className="text-amber-400 font-bold">HERD NUTRITION PRESCRIPTION</span>
              </>
            ) : actionState === 'greeting' ? (
              <>
                <Sparkles size={15} className="bubble-icon-pulse text-cyan-400" />
                <span className="text-cyan-300 font-bold">RAGUL DAIRY AI ASSISTANT</span>
              </>
            ) : (
              <>
                <Volume2 size={15} className="bubble-icon-pulse text-emerald-400" />
                <span className="text-emerald-300 font-bold">RAGUL EXPLAINING TO SIR</span>
              </>
            )}
          </div>
          <div className="bubble-body">
            "{lastAssistantMsg.length > 240 ? `${lastAssistantMsg.slice(0, 240)}...` : lastAssistantMsg}"
          </div>
        </div>
      )}

      {/* Floating Listening Indicator when User is speaking into Mic */}
      {isListening && !isSpeaking && (
        <div className="tom-speech-bubble bubble-listening-active">
          <div className="bubble-header">
            <Radio size={15} className="bubble-icon-pulse text-rose-400 animate-spin" />
            <span className="text-rose-300 font-semibold tracking-wide">LISTENING ATTENTIVELY...</span>
          </div>
          <div className="bubble-body text-slate-200">
            "I am listening to your voice, Sir. Please speak your farm query..."
          </div>
        </div>
      )}

      {/* Interruption Indicator */}
      {interrupted && (
        <div className="tom-interrupted-bubble">
          <Ear size={15} />
          <span>Listening to your question, Sir...</span>
        </div>
      )}

      {/* 3D Interactive Character Frame */}
      <div
        className={`ragul-character-wrapper ${
          isWakingUp
            ? 'tom-wakeup'
            : actionState === 'alert'
            ? 'tom-action-alert'
            : actionState === 'estrus'
            ? 'tom-action-estrus'
            : actionState === 'nutrition'
            ? 'tom-action-nutrition'
            : actionState === 'greeting'
            ? 'tom-action-greeting'
            : isSpeaking
            ? 'tom-talking-explaining'
            : isListening
            ? 'tom-listening-ear'
            : isProcessing
            ? 'tom-thinking-pulse'
            : 'tom-idle'
        } ${isPoked ? 'tom-poked' : ''}`}
        onClick={handleCharacterClick}
        title="Click Ragul to speak or interrupt!"
      >
        {/* Dynamic Multi-layered Lighting Aura */}
        <div
          className={`character-glow ${
            actionState === 'alert'
              ? 'alert-glow'
              : actionState === 'estrus'
              ? 'estrus-glow'
              : actionState === 'nutrition'
              ? 'nutrition-glow'
              : isSpeaking
              ? 'speaking-glow'
              : isListening
              ? 'listening-glow'
              : isProcessing
              ? 'thinking-glow'
              : isWakingUp
              ? 'wakeup-glow'
              : ''
          }`}
        />

        {/* Character Base Image */}
        <img
          src="/ragul_transparent.png"
          alt="3D Ragul AI Character in Coat Suit"
          className="ragul-fullbody-img"
        />

        {/* --- DYNAMIC INTERACTIVE POSE EFFECTS --- */}

        {/* 1. LISTENING EAR ACOUSTIC RADAR (When user speaks) */}
        {isListening && (
          <div className="hearing-ear-radar">
            <div className="sonar-ring ring-1" />
            <div className="sonar-ring ring-2" />
            <div className="sonar-ring ring-3" />
            <div className="ear-radar-core">
              <Ear size={16} className="text-rose-400" />
            </div>
            <span className="hearing-pill-label">LISTENING</span>
          </div>
        )}

        {/* 2. EXPLAINING TELEMETRY ORBIT (When Ragul speaks) */}
        {isSpeaking && (
          <div className="explaining-holo-badges">
            <div className="holo-orbit-item orbit-1" title="Milk Yield">
              <Milk size={13} className="text-cyan-400" />
            </div>
            <div className="holo-orbit-item orbit-2" title="Herd Health">
              <Activity size={13} className="text-emerald-400" />
            </div>
            <div className="holo-orbit-item orbit-3" title="Nutrition">
              <Wheat size={13} className="text-amber-400" />
            </div>
          </div>
        )}

        {/* 3. THINKING INDICATOR */}
        {isProcessing && (
          <div className="thinking-orb-indicator">
            <Sparkles size={20} className="text-amber-300 animate-spin" />
          </div>
        )}

        {/* Dynamic Status Tag at Bottom of Stage */}
        <div
          className={`character-mic-tag ${
            actionState === 'alert'
              ? 'tag-alert'
              : actionState === 'estrus'
              ? 'tag-estrus'
              : actionState === 'nutrition'
              ? 'tag-nutrition'
              : actionState === 'greeting'
              ? 'tag-greeting'
              : isListening
              ? 'mic-listening'
              : isSpeaking
              ? 'mic-speaking'
              : isProcessing
              ? 'mic-thinking'
              : ''
          }`}
        >
          {actionState === 'alert' ? (
            <span className="mic-badge-content badge-alert">
              <AlertTriangle size={14} /> CLINICAL ALERT
            </span>
          ) : actionState === 'estrus' ? (
            <span className="mic-badge-content badge-estrus">
              <HeartPulse size={14} /> HEAT CYCLE
            </span>
          ) : actionState === 'nutrition' ? (
            <span className="mic-badge-content badge-nutrition">
              <Wheat size={14} /> FEED SCHEDULE
            </span>
          ) : actionState === 'greeting' ? (
            <span className="mic-badge-content badge-greeting">
              <Sparkles size={14} /> ASSISTING SIR
            </span>
          ) : isListening ? (
            <span className="mic-badge-content badge-hearing">
              <Ear size={14} /> HEARING YOU...
            </span>
          ) : isSpeaking ? (
            <span className="mic-badge-content badge-explaining">
              <Volume2 size={14} /> EXPLAINING
            </span>
          ) : isProcessing ? (
            <span className="mic-badge-content badge-thinking">
              <Sparkles size={14} /> ANALYZING FARM...
            </span>
          ) : isWakingUp ? (
            <span className="mic-badge-content">
              <Sparkles size={14} /> WAKING UP!
            </span>
          ) : (
            <span className="mic-badge-content">
              <CheckCircle2 size={14} /> READY FOR SIR
            </span>
          )}
        </div>

        {/* Soundwave Shockwaves */}
        {(isSpeaking || isListening) && (
          <div className="tom-voice-rings">
            <span className="voice-ring ring-1" />
            <span className="voice-ring ring-2" />
            <span className="voice-ring ring-3" />
          </div>
        )}
      </div>

      {/* Live Equalizer Audio Visualizer */}
      <div className="tom-audio-equalizer">
        {[...Array(32)].map((_, i) => (
          <span
            key={i}
            className={`eq-bar ${isSpeaking || isListening ? 'active' : ''} ${
              isSpeaking
                ? 'eq-speaking'
                : isListening
                ? 'eq-listening'
                : isProcessing
                ? 'eq-thinking'
                : ''
            }`}
            style={{
              animationDelay: `${(i % 8) * 0.07}s`,
              height: isSpeaking
                ? `${18 + (i % 8) * 4}px`
                : isListening
                ? `${12 + (i % 5) * 3}px`
                : '4px'
            }}
          />
        ))}
      </div>

      {/* Big Central Glowing Mic Button */}
      <div className="stage-action-bar">
        <button
          onClick={onToggleMic}
          className={`big-voice-orb-btn ${isListening ? 'listening-active' : ''}`}
          title={isListening ? 'Click to stop listening' : 'Click to speak to Ragul'}
        >
          <div className="orb-ring" />
          {isListening ? <MicOff size={26} /> : <Mic size={26} />}
          <span className="orb-label">{isListening ? 'Stop Speaking' : 'Talk to Ragul'}</span>
        </button>
      </div>

      {/* Quick Interactive Dairy Query Chips */}
      {onSendQuery && (
        <div className="quick-query-pills">
          <span className="pills-title">Quick Inquiries:</span>
          <div className="pills-scroll">
            {quickQueries.map((item, idx) => (
              <button
                key={idx}
                onClick={() => onSendQuery(item.query)}
                className="query-pill-btn"
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
