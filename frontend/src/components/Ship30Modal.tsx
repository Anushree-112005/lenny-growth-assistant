import React, { useState } from 'react';
import { X, PenTool, Loader2, BookOpen, CheckCircle } from 'lucide-react';
import { Ship30Response } from '../types';

interface Ship30ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (topic: string) => Promise<Ship30Response>;
  onOpenArtifact: (artifactId: string) => void;
}

const PRESET_TOPICS = [
  "Self-sustaining product-led growth loops vs linear funnels",
  "The Four Fits Framework for scaling past Product-Market Fit",
  "Cohort retention curves and diagnosing true Product-Market Fit",
  "SaaS value metric selection and packaging pivot strategies",
];

export const Ship30Modal: React.FC<Ship30ModalProps> = ({
  isOpen,
  onClose,
  onGenerate,
  onOpenArtifact,
}) => {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Ship30Response | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (selectedTopic?: string) => {
    const targetTopic = selectedTopic || topic;
    if (!targetTopic.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await onGenerate(targetTopic.trim());
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Generation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <PenTool size={16} />
            <h3 className="modal-title">Ship 30 for 30 Long-Form Essay Skill</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={15} />
          </button>
        </div>

        <div className="modal-content">
          <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Craft an evidence-grounded, ~1,250-word Atomic Essay structured with an opening 1-3-1 hook,
            central thesis, skimmable headings, practical action steps, and citations linked to ingested transcripts.
          </p>

          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>
              SELECT EVIDENCE-BACKED TOPIC
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {PRESET_TOPICS.map((t, idx) => (
                <button
                  key={idx}
                  className="btn-header-action"
                  style={{ textAlign: 'left', justifyContent: 'flex-start' }}
                  onClick={() => {
                    setTopic(t);
                    handleSubmit(t);
                  }}
                  disabled={loading}
                >
                  <BookOpen size={12} />
                  <span>{t}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>
              OR TYPE CUSTOM TOPIC
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              <input
                type="text"
                placeholder="e.g. Why retention curves must flatten parallel to baseline"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: 6,
                  border: '1px solid var(--border-strong)',
                  fontSize: 13,
                  outline: 'none',
                }}
                disabled={loading}
              />
              <button
                className="btn-send"
                onClick={() => handleSubmit()}
                disabled={!topic.trim() || loading}
              >
                {loading ? <Loader2 size={14} className="spinner" /> : 'Generate'}
              </button>
            </div>
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-secondary)' }}>
              <Loader2 size={24} className="spinner" style={{ margin: '0 auto 8px' }} />
              <div style={{ fontSize: 13, fontWeight: 600 }}>Synthesizing ~1,250-Word Grounded Essay...</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                Retrieving transcript chunks, enforcing structure, and verifying citations.
              </div>
            </div>
          )}

          {error && (
            <div style={{ padding: 12, borderRadius: 6, background: '#fef2f2', color: 'var(--danger)', fontSize: 13 }}>
              {error}
            </div>
          )}

          {result && (
            <div style={{ borderTop: '1px solid var(--border-light)', paddingTop: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <CheckCircle size={15} style={{ color: 'var(--success)' }} />
                  <strong>{result.title}</strong>
                </div>
                <span className="relevance-badge">
                  {result.word_count} words | {result.citations.length} sources
                </span>
              </div>

              <div
                style={{
                  maxHeight: 180,
                  overflowY: 'auto',
                  fontSize: 12.5,
                  color: 'var(--text-secondary)',
                  background: 'var(--bg-secondary)',
                  padding: 10,
                  borderRadius: 6,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {result.essay}
              </div>

              {result.artifact_id && (
                <button
                  className="btn-new-chat"
                  style={{ width: '100%', marginTop: 12 }}
                  onClick={() => {
                    onOpenArtifact(result.artifact_id!);
                    onClose();
                  }}
                >
                  Inspect in Artifact Viewer
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
