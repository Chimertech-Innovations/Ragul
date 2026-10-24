import React, { useRef, useEffect, useState } from 'react';
import { User, Copy, Check, Sparkles, Volume2, Camera, Eye, X, Maximize2, ShieldCheck, BarChart2 } from 'lucide-react';
import { useRagulStore, ProofImageItem } from '../store/useRagulStore';
import { FarmVisualChart, ChartDataPayload } from './FarmVisualChart';

type ParsedContentBlock =
  | string
  | { type: 'chart'; data: ChartDataPayload }
  | { type: 'diagram'; content: string }
  | { type: 'table'; header: string[]; rows: string[][] };

// Clean text and render formatted elements nicely including visual charts, diagrammatic graphs & tables
const FormattedMessageContent: React.FC<{ content: string }> = ({ content }) => {
  // 1. Extract ```chart ... ``` JSON blocks first
  const chartRegex = /```(?:chart|json:chart)\s*([\s\S]*?)```/gi;
  const rawChartBlocks: { placeholder: string; data: ChartDataPayload }[] = [];
  let intermediate = content.replace(chartRegex, (_, jsonStr) => {
    try {
      const parsed = JSON.parse(jsonStr.trim());
      const placeholder = `__FARM_CHART_BLOCK_${rawChartBlocks.length}__`;
      rawChartBlocks.push({ placeholder, data: parsed });
      return `\n\n${placeholder}\n\n`;
    } catch (e) {
      return '';
    }
  });

  // 2. Clean out raw HTML tags like <br>, <p>, <b>
  let clean = intermediate
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/?[a-z][a-z0-9]*[^<>]*>/gi, '')
    .trim();

  // 3. Process lines for charts, diagrammatic ASCII boxes, and markdown tables
  const lines = clean.split('\n');
  const textBlocks: ParsedContentBlock[] = [];

  let inTable = false;
  let currentTableHeaders: string[] = [];
  let currentTableRows: string[][] = [];

  let inDiagram = false;
  let currentDiagramLines: string[] = [];

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

    // Check for chart block placeholder
    const matchedChart = rawChartBlocks.find(c => line.includes(c.placeholder));
    if (matchedChart) {
      if (inTable) {
        textBlocks.push({ type: 'table', header: currentTableHeaders, rows: currentTableRows });
        inTable = false;
        currentTableHeaders = [];
        currentTableRows = [];
      }
      if (inDiagram) {
        textBlocks.push({ type: 'diagram', content: currentDiagramLines.join('\n') });
        inDiagram = false;
        currentDiagramLines = [];
      }
      flushTextBuffer();
      textBlocks.push({ type: 'chart', data: matchedChart.data });
      continue;
    }

    // Check for diagrammatic ASCII borders or block meters (e.g. ┌─, ├─, └─, ████)
    const isDiagramBorder = line.startsWith('┌') || line.startsWith('├') || line.startsWith('└') || line.startsWith('+---') || line.startsWith('|===');
    const isDiagramContent = isDiagramBorder || (inDiagram && (line.startsWith('│') || line.startsWith('|') || line.includes('██') || line.includes('▓▓')));

    if (isDiagramContent) {
      if (inTable) {
        textBlocks.push({ type: 'table', header: currentTableHeaders, rows: currentTableRows });
        inTable = false;
        currentTableHeaders = [];
        currentTableRows = [];
      }
      flushTextBuffer();
      inDiagram = true;
      currentDiagramLines.push(rawLine);
      if (line.startsWith('└') || line.endsWith('+---') || (line.startsWith('+') && line.endsWith('+') && currentDiagramLines.length > 2)) {
        textBlocks.push({ type: 'diagram', content: currentDiagramLines.join('\n') });
        inDiagram = false;
        currentDiagramLines = [];
      }
      continue;
    } else if (inDiagram) {
      textBlocks.push({ type: 'diagram', content: currentDiagramLines.join('\n') });
      inDiagram = false;
      currentDiagramLines = [];
    }

    // Check if line is Markdown Table
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
  if (inDiagram && currentDiagramLines.length > 0) {
    textBlocks.push({ type: 'diagram', content: currentDiagramLines.join('\n') });
  }
  flushTextBuffer();


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
                  const startsWithEmoji = /^[\u{1F300}-\u{1FAD6}\u{2000}-\u{27BF}\u{FE00}-\u{FE0F}]/u.test(cleanLine);
                  return (
                    <div key={lIdx} className="clean-bullet-item">
                      {!startsWithEmoji && <span className="bullet-dot">▸</span>}
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
        } else if (block.type === 'chart') {
          return <FarmVisualChart key={idx} data={block.data} />;
        } else if (block.type === 'diagram') {
          return (
            <div key={idx} className="diagrammatic-ascii-card">
              <div className="diagram-card-header">
                <BarChart2 size={13} className="text-cyan-400" />
                <span>Diagrammatic Representation</span>
              </div>
              <pre className="diagrammatic-pre">{block.content}</pre>
            </div>
          );
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
                    onClick={() => {
                      const text = encodeURIComponent(`🐄 *PashuX Farm Update:*\n${msg.content}\n\n🤖 _Sent from RAGUL AI_`);
                      window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank');
                    }}
                    className="wa-icon-action-btn"
                    title="Share directly to WhatsApp"
                  >
                    <span>📲</span>
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

              {/* CCTV DETECTION PROOF GALLERY */}
              {proofImages.length > 0 && (
                <div className="cctv-proof-gallery-box">
                  <div className="cctv-proof-header">
                    <div className="cctv-proof-title">
                      <Camera size={14} className="text-cyan-400" />
                      <span>CCTV Detection Photo Proof ({proofImages.length})</span>
                    </div>
                    <span className="cctv-verified-badge">
                      <ShieldCheck size={12} /> AI Verified
                    </span>
                  </div>

                  <div className="cctv-proof-grid">
                    {proofImages.map((proof, pIdx) => (
                      <div
                        key={pIdx}
                        className="cctv-proof-card"
                        onClick={() => setActiveProofModal(proof)}
                        title="Click to zoom CCTV snapshot"
                      >
                        <div className="cctv-image-wrapper">
                          <img
                            src={proof.image_url}
                            alt={proof.description || 'CCTV Capture'}
                            className="cctv-proof-thumb"
                            loading="lazy"
                            onError={(e) => {
                              // Fallback placeholder if image load fails
                              (e.target as HTMLElement).style.display = 'none';
                            }}
                          />
                          <div className="cctv-zoom-overlay">
                            <Maximize2 size={16} />
                            <span>View Proof</span>
                          </div>
                          <span className="cctv-cam-tag">{proof.camera_id || 'CAM01'}</span>
                        </div>

                        <div className="cctv-card-meta">
                          <div className="cctv-meta-row">
                            <span className="cctv-cow-badge">🐮 {proof.cattle_id || 'Herd'}</span>
                            {proof.confidence && (
                              <span className="cctv-conf-badge">{proof.confidence}</span>
                            )}
                          </div>
                          {proof.time && (
                            <div className="cctv-time-label">⏰ Captured at {proof.time}</div>
                          )}
                          {proof.description && (
                            <div className="cctv-desc-snippet">{proof.description}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

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

      {/* FULL RESOLUTION PROOF LIGHTBOX MODAL */}
      {activeProofModal && (
        <div className="proof-lightbox-overlay" onClick={() => setActiveProofModal(null)}>
          <div className="proof-lightbox-dialog" onClick={(e) => e.stopPropagation()}>
            <button className="proof-close-btn" onClick={() => setActiveProofModal(null)}>
              <X size={20} />
            </button>

            <div className="proof-lightbox-header">
              <div className="proof-header-info">
                <span className="proof-title-tag">📸 CCTV Vision Capture Proof</span>
                <h3>{activeProofModal.cattle_id || 'Cattle'} • {activeProofModal.camera_id || 'CAM01'}</h3>
              </div>
              {activeProofModal.confidence && (
                <span className="proof-modal-confidence">
                  AI Confidence: {activeProofModal.confidence}
                </span>
              )}
            </div>

            <div className="proof-modal-image-container">
              <img
                src={activeProofModal.image_url}
                alt={activeProofModal.description || 'CCTV Proof Full'}
                className="proof-modal-full-img"
              />
            </div>

            <div className="proof-modal-footer">
              <div className="proof-footer-desc">
                <strong>Detection Summary:</strong> {activeProofModal.description}
              </div>
              {activeProofModal.time && (
                <div className="proof-footer-time">Recorded Time: {activeProofModal.time}</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
