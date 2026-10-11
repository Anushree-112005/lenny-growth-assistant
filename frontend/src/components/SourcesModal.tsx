import React from 'react';
import { X, Database, ExternalLink, Headphones, Newspaper } from 'lucide-react';
import { SourceDocument } from '../types';

interface SourcesModalProps {
  isOpen: boolean;
  onClose: () => void;
  sources: SourceDocument[];
}

export const SourcesModal: React.FC<SourcesModalProps> = ({ isOpen, onClose, sources }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Database size={16} />
            <h3 className="modal-title">Ingested Transcript Sources ({sources.length})</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={15} />
          </button>
        </div>

        <div className="modal-content">
          <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            The assistant grounds all insights strictly in these verified transcript documents. Unverified claims
            are prohibited by the grounding engine.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {sources.map((src) => (
              <div
                key={src.id}
                style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-light)',
                  padding: '12px 14px',
                  borderRadius: 8,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600, fontSize: 13.5 }}>
                    {src.source_type === 'podcast' ? <Headphones size={14} /> : <Newspaper size={14} />}
                    <span>{src.title}</span>
                  </div>
                  <span className="relevance-badge">{src.chunks_count} chunks</span>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', gap: 12, marginTop: 4 }}>
                  <span>Author: {src.author}</span>
                  <span>ID: {src.id}</span>
                  {src.url && (
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: 'var(--accent)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 2 }}
                    >
                      Source <ExternalLink size={10} />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
