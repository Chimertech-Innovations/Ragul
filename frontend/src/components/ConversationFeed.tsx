import React, { useRef, useEffect, useState } from 'react';
import { User, Copy, Check, Sparkles, Volume2, Camera, Eye, X, ShieldCheck } from 'lucide-react';
import { useRagulStore, ProofImageItem } from '../store/useRagulStore';

type ParsedContentBlock =
  | string
  | { type: 'table'; header: string[]; rows: string[][] };

const EMOJI_AND_SYMBOLS_REGEX = /[\p{Extended_Pictographic}\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}]/gu;

// Clean text and render formatted elements with rich bold text and clean inline bullets
const FormattedMessageContent: React.FC<{ content: string }> = ({ content }) => {
  // 1. Strip any legacy chart blocks or code fences, HTML tags, but preserve **bold markdown**
  let clean = content
    .replace(/```(?:chart|json:chart|json|[\w-]+)?\s*[\s\S]*?```/gi, '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/?[a-z][a-z0-9]*[^<>]*>/gi, '')
    .replace(EMOJI_AND_SYMBOLS_REGEX, '')
    .trim();

  // Helper to format inline text: bold markdown **text** rendered as <strong>, with clean spacing
  const renderFormattedInline = (lineText: string) => {
    if (!lineText) return null;
    const parts = lineText.split(/(\*\*[^*]+?\*\*)/g);
    return parts.map((part, pIdx) => {
      if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
        const boldText = part.slice(2, -2).trim();
        const prevPart = pIdx > 0 ? parts[pIdx - 1] : '';
        const nextPart = pIdx < parts.length - 1 ? parts[pIdx + 1] : '';

        // Add leading space if previous plain part didn't end with whitespace or opening quote/bracket
        const needsLeadingSpace = pIdx > 0 && prevPart.length > 0 && !/[\s(\["']$/.test(prevPart);
        // Add trailing space if next plain part doesn't start with whitespace or punctuation
        const needsTrailingSpace = pIdx < parts.length - 1 && nextPart.length > 0 && !/^[\s,.:;!?)\]"']/.test(nextPart);

        return (
          <React.Fragment key={pIdx}>
            {needsLeadingSpace ? ' ' : null}
            <strong className="font-semibold text-slate-900 dark:text-emerald-300">
              {boldText}
            </strong>
            {needsTrailingSpace ? ' ' : null}
          </React.Fragment>
        );
      }
      // Remove any stray single asterisks
      const plain = part.replace(/\*/g, '');
      return <React.Fragment key={pIdx}>{plain}</React.Fragment>;
    });
  };

  // 2. Process lines for standard text and clean markdown tables, stripping ASCII diagram boxes
  const lines = clean.split('\n');
  const textBlocks: ParsedContentBlock[] = [];

  let inTable = false;
  let currentTableHeaders: string[] = [];
  let currentTableRows: string[][] = [];
  let currentTextBuffer: string[] = [];

  const flushTextBuffer = () => {
    if (currentTextBuffer.length > 0) {
      textBlocks.push(currentTextBuffer.join('\n'));
      currentTextBuffer = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const line = rawLine.trim();

    // Skip diagrammatic ASCII borders and box meter lines
    if (
      line.startsWith('┌') || 
      line.startsWith('├') || 
      line.startsWith('└') || 
      line.startsWith('+---') || 
      line.startsWith('|===') ||
      (line.startsWith('│') && line.endsWith('│')) ||
      line.includes('███')
    ) {
      continue;
    }

    // Check if line is standard Markdown Table
    if (line.startsWith('|') && line.endsWith('|')) {
      const cells = line.split('|').map(c => c.trim()).filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
      const isSeparator = cells.every(c => /^[-:\s]+$/.test(c));

      if (!inTable) {
        flushTextBuffer();
        inTable = true;
        currentTableHeaders = cells;
      } else if (!isSeparator) {
        currentTableRows.push(cells);
      }
    } else {
      if (inTable) {
        textBlocks.push({ type: 'table', header: currentTableHeaders, rows: currentTableRows });
        inTable = false;
        currentTableHeaders = [];
        currentTableRows = [];
      }
      currentTextBuffer.push(rawLine);
    }
  }

  if (inTable && currentTableHeaders.length > 0) {
    textBlocks.push({ type: 'table', header: currentTableHeaders, rows: currentTableRows });
  }
  flushTextBuffer();

  // Render text block with bold keywords, bold headings, and clean inline bullets
  const renderTextParagraph = (text: string, blockKey: number) => {
    const paragraphs = text.split('\n\n');
    return (
      <div key={blockKey} className="message-text-group">
        {paragraphs.map((p, pIdx) => {
          const pLines = p.split('\n');
          return (
            <div key={pIdx} className="message-paragraph">
              {pLines.map((line, lIdx) => {
                const trimmed = line.trim();
                if (!trimmed) return null;
                const isBullet = /^([•▸\-]|(?:\*(?!\*)))/.test(trimmed);
                const cleanLine = isBullet ? trimmed.replace(/^([•▸\-]|(?:\*(?!\*)))\s*/, '') : trimmed;

                if (!cleanLine) return null;

                if (isBullet) {
                  return (
                    <div key={lIdx} className="flex items-start gap-2 my-1 leading-relaxed text-slate-800 dark:text-slate-200">
                      <span className="text-emerald-500 font-bold shrink-0 mt-[2px] select-none text-xs">▸</span>
                      <span className="flex-1">{renderFormattedInline(cleanLine)}</span>
                    </div>
                  );
                }

                return (
                  <p key={lIdx} className="my-1.5 leading-relaxed text-slate-800 dark:text-slate-200">
                    {renderFormattedInline(cleanLine)}
                  </p>
                );
              })}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="formatted-message-content">
      {textBlocks.map((block, idx) => {
        if (typeof block === 'string') {
          return renderTextParagraph(block, idx);
        } else if (block.type === 'table') {
          return (
            <div key={idx} className="glassmorphic-table-container">
              <table className="clean-chat-table">
                <thead>
                  <tr>
                    {block.header.map((h, hIdx) => (
                      <th key={hIdx}>{renderFormattedInline(h)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {block.rows.map((row, rIdx) => (
                    <tr key={rIdx}>
                      {row.map((cell, cIdx) => (
                        <td key={cIdx}>
                          {renderFormattedInline(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }
        return null;
      })}
    </div>
  );
};

export const ConversationFeed: React.FC = () => {
  const { messages, isProcessing, isSpeaking } = useRagulStore();
  const feedEndRef = useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [activeProofModal, setActiveProofModal] = useState<ProofImageItem | null>(null);

  useEffect(() => {
    feedEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  const copyToClipboard = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="conversation-feed">
      {messages.map((msg, index) => {
        const isLatestRagul = msg.role === 'assistant' && index === messages.length - 1;
        
        // Extract proof images from message or tool metadata
        const proofImages: ProofImageItem[] = 
          (msg.proof_images && msg.proof_images.length > 0)
            ? msg.proof_images
            : (msg.tool_meta?.proof_images || msg.tool_meta?.result?.proof_images || []);

        return (
          <div key={msg.id} className={`message-card ${msg.role} ${isLatestRagul && isSpeaking ? 'is-speaking-active' : ''}`}>
            <div className="message-header">
              <div className="sender-badge">
                {msg.role === 'user' ? (
                  <div className="chat-avatar-user"><User size={13} /></div>
                ) : (
                  <div className="ragul-avatar-container">
                    <img src="/ragul_transparent.png" alt="Ragul" className="chat-avatar-ragul" />
                    {isLatestRagul && isSpeaking && <span className="speaking-status-dot" />}
                  </div>
                )}
                <span className="role-tag">{msg.role === 'user' ? 'Sir' : 'RAGUL AI'}</span>
                {isLatestRagul && isSpeaking && (
                  <span className="speaking-badge-compact">
                    <Volume2 size={11} className="pulse-icon" />
                    <span>Speaking</span>
                  </span>
                )}
              </div>
              <div className="message-actions">
                <span className="timestamp-tag">{msg.timestamp}</span>
                
                {msg.role === 'assistant' && (
                  <button
                    onClick={() => copyToClipboard(msg.id, msg.content)}
                    className="copy-btn"
                    title="Copy response"
                  >
                    {copiedId === msg.id ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
                  </button>
                )}
              </div>
            </div>

            {/* Message Body Content */}
            <div className="message-body">
              <FormattedMessageContent content={msg.content} />
            </div>

            {/* CCTV Proof Photos Gallery */}
            {proofImages.length > 0 && (
              <div className="proof-gallery-box">
                <div className="proof-gallery-title">
                  <Camera size={13} className="text-cyan-400" />
                  <span>AI Visual Detection Evidence ({proofImages.length} Proof Images):</span>
                </div>
                <div className="proof-cards-grid">
                  {proofImages.map((img, pIdx) => (
                    <div
                      key={pIdx}
                      className="proof-image-thumb-card"
                      onClick={() => setActiveProofModal(img)}
                      title="Click to zoom CCTV Evidence"
                    >
                      <img 
                        src={img.image_url} 
                        alt="CCTV Detection" 
                        className="thumb-img" 
                        onError={(e) => {
                          (e.currentTarget as HTMLElement).style.display = 'none';
                        }}
                      />
                      <div className="thumb-overlay">
                        <Eye size={16} />
                      </div>
                      <div className="thumb-badge">
                        <span>{img.cattle_id || 'Cattle'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Thinking / Analyzing Indicator */}
      {isProcessing && (
        <div className="message-card assistant is-thinking">
          <div className="message-header">
            <div className="sender-badge">
              <div className="ragul-avatar-container">
                <img src="/ragul_transparent.png" alt="Ragul" className="chat-avatar-ragul animate-pulse" />
              </div>
              <span className="role-tag">RAGUL AI</span>
            </div>
          </div>
          <div className="thinking-loader">
            <Sparkles size={16} className="text-amber-400 animate-spin" />
            <span>Analyzing farm cameras, herd database, and health metrics...</span>
          </div>
        </div>
      )}

      <div ref={feedEndRef} />

      {/* High-Resolution Modal for Proof Photos */}
      {activeProofModal && (
        <div className="proof-zoom-modal" onClick={() => setActiveProofModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">
                <ShieldCheck size={16} className="text-emerald-400" />
                <span>Verified CCTV Evidence - {activeProofModal.cattle_id || 'Cattle'}</span>
              </div>
              <button onClick={() => setActiveProofModal(null)} className="modal-close-btn">
                <X size={18} />
              </button>
            </div>
            <div className="modal-image-wrapper">
              <img src={activeProofModal.image_url} alt="Proof" className="zoomed-img" />
            </div>
            <div className="modal-meta-info">
              {activeProofModal.description && <p className="meta-desc">{activeProofModal.description}</p>}
              <div className="meta-pills">
                {activeProofModal.confidence && (
                  <span className="meta-pill">Confidence: <strong>{activeProofModal.confidence}</strong></span>
                )}
                {activeProofModal.camera_id && (
                  <span className="meta-pill">Camera: <strong>{activeProofModal.camera_id}</strong></span>
                )}
                {activeProofModal.time && (
                  <span className="meta-pill">Time: <strong>{activeProofModal.time}</strong></span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
