import React, { useRef, useEffect, useState } from 'react';
import { User, Copy, Check, Sparkles, Volume2 } from 'lucide-react';
import { useRagulStore } from '../store/useRagulStore';

// Clean text and render formatted elements nicely without raw HTML tags or markdown noise
const FormattedMessageContent: React.FC<{ content: string }> = ({ content }) => {
  // 1. Clean out raw HTML tags like <br>, <br/>, <p>, <b>
  let clean = content
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/?[a-z][a-z0-9]*[^<>]*>/gi, '')
    .trim();

  // 2. Check if content contains markdown table
  const lines = clean.split('\n');
  const tableLines: string[] = [];
  const textBlocks: (string | { type: 'table'; header: string[]; rows: string[][] })[] = [];

  let inTable = false;
  let currentTableHeaders: string[] = [];
  let currentTableRows: string[][] = [];
  let currentTextBuffer: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('|') && line.endsWith('|')) {
      const cells = line.split('|').map(c => c.trim()).filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
      
      // Is separator row |---|---|
      const isSeparator = cells.every(c => /^[-:\s]+$/.test(c));

      if (!inTable) {
        if (currentTextBuffer.length > 0) {
          textBlocks.push(currentTextBuffer.join('\n'));
          currentTextBuffer = [];
        }
        inTable = true;
        currentTableHeaders = cells;
      } else if (!isSeparator) {
        currentTableRows.push(cells);
      }
    } else {
      if (inTable) {
        textBlocks.push({
          type: 'table',
          header: currentTableHeaders,
          rows: currentTableRows
        });
        inTable = false;
        currentTableHeaders = [];
        currentTableRows = [];
      }
      currentTextBuffer.push(lines[i]);
    }
  }

  if (inTable && currentTableHeaders.length > 0) {
    textBlocks.push({
      type: 'table',
      header: currentTableHeaders,
      rows: currentTableRows
    });
  } else if (currentTextBuffer.length > 0) {
    textBlocks.push(currentTextBuffer.join('\n'));
  }

  // Render text block with bold formatting and clean bullet lists
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
                const isBullet = trimmed.startsWith('•') || trimmed.startsWith('- ') || trimmed.startsWith('* ');
                const cleanLine = isBullet ? trimmed.replace(/^[•\-\*]\s*/, '') : trimmed;

                // Parse bold **text**
                const parts = cleanLine.split(/(\*\*[^*]+\*\*)/g);

                const renderedLine = parts.map((part, partIdx) => {
                  if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={partIdx} className="highlight-bold">{part.slice(2, -2)}</strong>;
                  }
                  return part;
                });

                if (isBullet) {
                  return (
                    <div key={lIdx} className="clean-bullet-item">
                      <span className="bullet-dot">▸</span>
                      <span className="bullet-text">{renderedLine}</span>
                    </div>
                  );
                }

                return (
                  <p key={lIdx} className="clean-text-line">
                    {renderedLine}
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
                      <th key={hIdx}>{h.replace(/\*\*/g, '')}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {block.rows.map((row, rIdx) => (
                    <tr key={rIdx}>
                      {row.map((cell, cIdx) => (
                        <td key={cIdx}>
                          {cell.split(/(\*\*[^*]+\*\*)/g).map((p, pIdx) =>
                            p.startsWith('**') && p.endsWith('**') ? (
                              <strong key={pIdx} className="highlight-bold">{p.slice(2, -2)}</strong>
                            ) : (
                              p
                            )
                          )}
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
        return (
          <div key={msg.id} className={`message-card ${msg.role} ${isLatestRagul && isSpeaking ? 'is-speaking-active' : ''}`}>
            <div className="message-header">
              <div className="sender-badge">
                {msg.role === 'user' ? (
                  <div className="chat-avatar-user"><User size={13} /></div>
                ) : (
                  <img src="/ragul_transparent.png" alt="Ragul" className="chat-avatar-ragul" />
                )}
                <span className="role-tag">{msg.role === 'user' ? 'Sir' : 'RAGUL AI'}</span>
                {msg.role === 'assistant' && (
                  <span className="ai-smart-chip">
                    <Sparkles size={11} />
                    <span>Dairy Intelligence</span>
                  </span>
                )}
              </div>
              <div className="message-actions">
                {isLatestRagul && isSpeaking && (
                  <span className="speaking-badge">
                    <Volume2 size={12} className="pulse-icon" />
                    <span>Speaking</span>
                  </span>
                )}
                <span className="timestamp-tag">{msg.timestamp}</span>
                
                {/* Direct WhatsApp Share Button for every assistant message */}
                {msg.role === 'assistant' && (
                  <button
                    onClick={() => {
                      const text = encodeURIComponent(`🐄 *Green Valley Farm Update:*\n${msg.content}\n\n🤖 _Sent from RAGUL AI_`);
                      window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank');
                    }}
                    className="wa-share-btn"
                    title="Share directly to WhatsApp"
                  >
                    <span className="wa-icon">📲</span>
                    <span className="wa-text">WhatsApp</span>
                  </button>
                )}

                <button
                  onClick={() => copyToClipboard(msg.id, msg.content)}
                  className="copy-btn"
                  title="Copy message"
                >
                  {copiedId === msg.id ? <Check size={12} className="copied" /> : <Copy size={12} />}
                </button>
              </div>
            </div>

            <div className="message-body">
              <FormattedMessageContent content={msg.content} />

              {/* Special WhatsApp URL Action Card if tool was invoked */}
              {msg.tool_meta?.whatsapp_url && (
                <div className="whatsapp-action-card">
                  <div className="wa-card-header">
                    <span className="wa-card-icon">📱</span>
                    <span className="wa-card-title">WhatsApp Report Ready</span>
                  </div>
                  <a
                    href={msg.tool_meta.whatsapp_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="wa-direct-link-btn"
                  >
                    <span>Open in WhatsApp</span>
                    <span>➔</span>
                  </a>
                </div>
              )}
            </div>
          </div>
        );
      })}

      {isProcessing && (
        <div className="message-card assistant thinking-card">
          <div className="message-header">
            <div className="sender-badge">
              <img src="/ragul_transparent.png" alt="Ragul" className="chat-avatar-ragul spin-slow" />
              <span className="role-tag">RAGUL AI</span>
            </div>
          </div>
          <div className="thinking-indicator">
            <span className="pulse-dot" />
            <span>Analyzing farm telemetry & formulating response...</span>
          </div>
        </div>
      )}

      <div ref={feedEndRef} />
    </div>
  );
};
