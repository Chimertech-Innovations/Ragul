import React from 'react';
import { Mic, Volume2, Sparkles, AlertCircle, MessageSquare } from 'lucide-react';
import { useRagulStore } from '../store/useRagulStore';

interface RagulAvatarProps {
  onToggleMic: () => void;
}

export const RagulAvatar: React.FC<RagulAvatarProps> = ({ onToggleMic }) => {
  const { isListening, isSpeaking, isProcessing, interrupted, messages } = useRagulStore();

  const lastAssistantMsg = [...messages].reverse().find((m) => m.role === 'assistant')?.content;

  return (
    <div className="ragul-avatar-stage">
      {/* Dynamic Background Glow Halo */}
      <div
        className={`avatar-halo ${isListening ? 'listening-halo' : isSpeaking ? 'speaking-halo' : isProcessing ? 'processing-halo' : ''}`}
      />

      {/* Main Avatar Card Container */}
      <div
        className={`avatar-card ${isListening ? 'listening' : isSpeaking ? 'speaking' : ''}`}
        onClick={onToggleMic}
        title={isListening ? 'Click to Mute' : isSpeaking ? 'Click to Interrupt' : 'Click to Speak with Ragul'}
      >
        <div className="avatar-image-wrapper">
          <img
            src="/ragul_avatar.png"
            alt="Ragul AI Assistant"
            className={`ragul-image ${isSpeaking ? 'ragul-talking' : isListening ? 'ragul-listening' : 'ragul-idle'}`}
          />

          {/* Floating Microphone Indicator Badge */}
          <div className={`avatar-mic-badge ${isListening ? 'badge-listening' : isSpeaking ? 'badge-speaking' : ''}`}>
            {isListening ? (
              <Mic size={18} className="icon-pulse" />
            ) : isSpeaking ? (
              <Volume2 size={18} className="icon-bounce" />
            ) : (
              <Sparkles size={16} />
            )}
          </div>

          {/* Holographic Speaker Tag */}
          <div className="avatar-identity-badge">
            <span className="live-dot" style={{ backgroundColor: isListening ? 'var(--accent-rose)' : isSpeaking ? 'var(--accent-emerald)' : 'var(--accent-cyan)' }} />
            <span>RAGUL • {isListening ? 'LISTENING...' : isSpeaking ? 'SPEAKING' : isProcessing ? 'THINKING...' : 'LIVE ASSISTANT'}</span>
          </div>
        </div>

        {/* Live Speaking Waves */}
        <div className="soundwave-meter">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className={`soundwave-pillar ${isSpeaking || isListening ? 'active' : ''}`}
              style={{
                animationDelay: `${(i % 5) * 0.12}s`,
                height: isSpeaking ? `${12 + (i % 6) * 5}px` : isListening ? `${8 + (i % 4) * 4}px` : '4px'
              }}
            />
          ))}
        </div>
      </div>

      {/* Dynamic Speech Bubble Callout */}
      {isSpeaking && lastAssistantMsg && (
        <div className="ragul-speech-bubble">
          <div className="speech-bubble-header">
            <MessageSquare size={13} color="var(--accent-emerald)" />
            <span>Ragul is answering live:</span>
          </div>
          <div className="speech-bubble-text">
            {lastAssistantMsg.length > 140 ? lastAssistantMsg.substring(0, 140) + '...' : lastAssistantMsg}
          </div>
        </div>
      )}

      {interrupted && (
        <div className="interruption-tag" style={{ marginTop: '12px' }}>
          <AlertCircle size={14} />
          <span>Interrupted: Ragul stopped talking to listen to you!</span>
        </div>
      )}
    </div>
  );
};
