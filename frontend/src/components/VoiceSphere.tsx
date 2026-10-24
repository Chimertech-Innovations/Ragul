import React from 'react';
import { Mic, MicOff, Volume2, Sparkles, AlertCircle } from 'lucide-react';
import { useRagulStore } from '../store/useRagulStore';

interface VoiceSphereProps {
  onToggleMic: () => void;
}

export const VoiceSphere: React.FC<VoiceSphereProps> = ({ onToggleMic }) => {
  const { isListening, isSpeaking, vadStatus, interrupted } = useRagulStore();

  return (
    <div className="voice-sphere-section">
      <div className="orb-container" onClick={onToggleMic} title={isListening ? "Click to Mute Mic" : "Click to Speak"}>
        <div className={`orb-ring ${isListening ? 'active' : ''}`} />
        <div className={`orb-core ${isListening ? 'listening' : isSpeaking ? 'speaking' : ''}`}>
          {isListening ? (
            <Mic size={36} />
          ) : isSpeaking ? (
            <Volume2 size={36} />
          ) : (
            <Sparkles size={34} />
          )}
        </div>
      </div>

      <div className="waveform-bars">
        {[...Array(16)].map((_, i) => (
          <div
            key={i}
            className={`wave-bar ${isSpeaking || (isListening && vadStatus === 'speech') ? 'active' : ''}`}
            style={{
              animationDelay: `${i * 0.08}s`,
              height: isSpeaking ? `${8 + (i % 4) * 7}px` : (isListening && vadStatus === 'speech') ? `${12 + (i % 5) * 8}px` : '6px',
              backgroundColor: (isListening && vadStatus === 'speech') ? '#10b981' : undefined
            }}
          />
        ))}
      </div>

      <div style={{
        marginTop: '12px',
        fontSize: '0.85rem',
        fontWeight: 600,
        color: isSpeaking
          ? 'var(--accent-emerald)'
          : isListening
            ? (vadStatus === 'speech' ? '#10b981' : vadStatus === 'processing' ? '#3b82f6' : 'var(--text-secondary)')
            : 'var(--text-secondary)'
      }}>
        {isSpeaking
          ? 'RAGUL Speaking (Start talking anytime to interrupt)'
          : isListening
            ? (vadStatus === 'speech'
                ? 'Voice Active: Speaking detected...'
                : vadStatus === 'processing'
                  ? 'Transcribing speech...'
                  : 'Listening (Noise Filtered: Silero VAD armed - speak anytime)')
            : 'Click Orb or Mic below to talk'}
      </div>

      {interrupted && (
        <div className="interruption-tag">
          <AlertCircle size={14} />
          <span>Jarvis Interruption: Cut off assistant voice immediately</span>
        </div>
      )}
    </div>
  );
};
