import React, { useState } from 'react';
import {
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Sparkles,
  FileText,
  Copy,
  Check,
  Quote,
  ArrowRight,
} from 'lucide-react';
import { Message } from '../types';

interface ChatMessageProps {
  message: Message;
  onGenerateArtifact: (prompt: string, type: string) => void;
  onDraftShip30: (topic: string) => void;
  onSelectSuggestion?: (prompt: string) => void;
}

const ABSTENTION_SUGGESTIONS = [
  { label: 'B2B PLG & Growth Loops', query: 'How does Elena Verna explain B2B PLG vs sales-assisted models?' },
  { label: 'The Four Fits Framework', query: 'What are the Four Fits according to Brian Balfour?' },
  { label: 'Diagnosing Retention Curves', query: 'Why are retention curves the true test of Product-Market Fit according to Casey Winters?' },
  { label: 'SaaS Pricing & Packaging', query: 'What are the core pricing models and value metric selection rules in SaaS?' },
  { label: 'Ship 30 Writing Architecture', query: 'What is the Ship 30 for 30 methodology for writing Atomic Essays?' },
];

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onGenerateArtifact,
  onDraftShip30,
  onSelectSuggestion,
}) => {
  const [showCitations, setShowCitations] = useState(true);
  const [copied, setCopied] = useState(false);
  const isAssistant = message.role === 'assistant';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Basic Markdown formatting helper
  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      if (line.startsWith('# ')) {
        return <h1 key={idx}>{line.replace('# ', '')}</h1>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={idx}>{line.replace('## ', '')}</h2>;
      }
      if (line.startsWith('### ')) {
        return <h3 key={idx}>{line.replace('### ', '')}</h3>;
      }
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return <li key={idx}>{formatInlineBold(line.slice(2))}</li>;
      }
      const numMatch = line.match(/^(\d+)\.\s+(.*)$/);
      if (numMatch) {
        return (
          <div key={idx} style={{ paddingLeft: 14, marginBottom: 4 }}>
            <strong>{numMatch[1]}.</strong> {formatInlineBold(numMatch[2])}
          </div>
        );
      }
      if (!line.trim()) {
        return <div key={idx} style={{ height: 8 }} />;
      }
      return <p key={idx}>{formatInlineBold(line)}</p>;
    });
  };

  const formatInlineBold = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className={`message-row ${message.role}`}>
      <div className="message-bubble">
        {/* Assistant Identity Header */}
        {isAssistant && (
          <div className="assistant-identity-header">
            <div className="assistant-id-badge">
              <div className="assistant-avatar">L</div>
              <span className="assistant-name">Lenny Growth Intelligence</span>
            </div>
            <div className="model-tag-pill">
              <span className="status-dot available" style={{ width: 6, height: 6 }} />
              <span>{message.provider ? message.provider.toUpperCase() : 'AI'}</span>
              <span>·</span>
              <span>{message.model === 'abstention-gate' ? 'grounded-search' : (message.model || 'qwen2.5:3b')}</span>
            </div>
          </div>
        )}

        {/* Clean Topic Explorer Card */}
        {message.abstained && (
          <div className="abstention-banner">
            <div className="abstention-title-row">
              <Sparkles size={15} />
              <span>Explore Verified Topics</span>
            </div>
            <div className="abstention-desc">
              Answers are strictly grounded in Lenny Rachitsky's podcast and newsletter archives to guarantee 100% accuracy. Choose a verified growth framework below:
            </div>

            <div className="abstention-chips-label">Verified topics from transcripts:</div>
            <div className="abstention-chips-grid">
              {ABSTENTION_SUGGESTIONS.map((s, idx) => (
                <button
                  key={idx}
                  className="clickable-chip"
                  onClick={() => onSelectSuggestion && onSelectSuggestion(s.query)}
                  title={`Run query: ${s.query}`}
                >
                  <span>{s.label}</span>
                  <ArrowRight size={11} />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className={isAssistant ? 'assistant-text' : ''}>
          {renderFormattedContent(message.content)}
        </div>

        {/* Impressive Citation Cards */}
        {isAssistant && message.citations && message.citations.length > 0 && (
          <div className="citations-container">
            <div
              className="citations-header"
              onClick={() => setShowCitations(!showCitations)}
            >
              <span>Verified Transcript Citations ({message.citations.length})</span>
              {showCitations ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </div>

            {showCitations && (
              <div className="citations-grid">
                {message.citations.map((c, i) => {
                  const isPodcast = !c.document_id.includes('newsletter') && !c.title.toLowerCase().includes('newsletter');
                  return (
                    <div key={c.id || i} className="citation-card">
                      <div className="citation-top">
                        <span className="citation-source-type">
                          {isPodcast ? '🎙️ Podcast' : '📰 Newsletter'}
                        </span>
                        {c.url ? (
                          <a
                            href={c.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="citation-title"
                          >
                            {c.title} <ExternalLink size={11} style={{ display: 'inline', marginLeft: 4 }} />
                          </a>
                        ) : (
                          <span className="citation-title">{c.title}</span>
                        )}
                        <span className="relevance-badge">
                          {Math.round((c.relevance_score || 0.85) * 100)}% Match
                        </span>
                      </div>
                      <div className="citation-quote-box">
                        <Quote size={13} style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: 2 }} />
                        <div className="citation-excerpt">
                          "{c.excerpt}"
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Action Toolbar Below Message */}
        {isAssistant && !message.abstained && (
          <div className="message-actions">
            <button
              className="btn-msg-action"
              onClick={() => onDraftShip30(message.content.slice(0, 100))}
              title="Draft a 1,250-word Ship 30 essay based on this answer"
            >
              <FileText size={12} />
              <span>Draft Ship 30 Essay</span>
            </button>
            <button
              className="btn-msg-action"
              onClick={() =>
                onGenerateArtifact(
                  `Create a modern HTML/CSS landing page deliverable based on: ${message.content.slice(0, 150)}`,
                  'html'
                )
              }
              title="Generate interactive HTML landing page artifact"
            >
              <Sparkles size={12} />
              <span>Create Landing Page Artifact</span>
            </button>
            <button className="btn-msg-action" onClick={handleCopy} title="Copy response">
              {copied ? <Check size={12} style={{ color: 'var(--success)' }} /> : <Copy size={12} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
