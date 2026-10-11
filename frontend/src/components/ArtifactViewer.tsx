import React, { useState } from 'react';
import { X, Copy, Download, ShieldCheck, Check, Code, Eye } from 'lucide-react';
import { ArtifactDetail } from '../types';

interface ArtifactViewerProps {
  artifact: ArtifactDetail | null;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);

  if (!artifact) {
    return (
      <aside className="artifact-panel">
        <div className="artifact-header">
          <div className="artifact-panel-title">Artifact Viewer</div>
          <button className="btn-icon" onClick={onClose}>
            <X size={15} />
          </button>
        </div>
        <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
          No deliverable selected. Ask a question or click "Create Landing Page Artifact" to generate deliverables.
        </div>
      </aside>
    );
  }

  const isHtml = artifact.artifact_type.toLowerCase() === 'html';

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = isHtml ? 'html' : 'md';
    const blob = new Blob([artifact.content], { type: isHtml ? 'text/html' : 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.toLowerCase().replace(/[^a-z0-9]/g, '-')}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <aside className="artifact-panel">
      {/* Header */}
      <div className="artifact-header">
        <div className="artifact-title-wrapper">
          <span className="artifact-type-badge">{artifact.artifact_type}</span>
          <span className="artifact-panel-title" title={artifact.title}>
            {artifact.title}
          </span>
        </div>
        <div className="artifact-controls">
          <button className="btn-icon" onClick={handleCopy} title="Copy raw code">
            {copied ? <Check size={14} style={{ color: 'var(--success)' }} /> : <Copy size={14} />}
          </button>
          <button className="btn-icon" onClick={handleDownload} title="Download file">
            <Download size={14} />
          </button>
          <button className="btn-icon" onClick={onClose} title="Close viewer">
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="artifact-tabs">
        <button
          className={`artifact-tab ${activeTab === 'preview' ? 'active' : ''}`}
          onClick={() => setActiveTab('preview')}
        >
          <Eye size={12} style={{ display: 'inline', marginRight: 4 }} />
          Preview
        </button>
        <button
          className={`artifact-tab ${activeTab === 'code' ? 'active' : ''}`}
          onClick={() => setActiveTab('code')}
        >
          <Code size={12} style={{ display: 'inline', marginRight: 4 }} />
          Source Code
        </button>
      </div>

      {/* Body */}
      <div className="artifact-body">
        {activeTab === 'preview' ? (
          isHtml ? (
            /* Sandboxed iframe strictly isolated without allow-same-origin to prevent session access */
            <iframe
              className="sandboxed-iframe"
              title="Artifact Preview"
              srcDoc={artifact.content}
              sandbox="allow-scripts"
            />
          ) : (
            <div className="artifact-code-view" style={{ whiteSpace: 'pre-wrap', fontFamily: 'var(--font-sans)', fontSize: 13.5, lineHeight: 1.6 }}>
              {artifact.content}
            </div>
          )
        ) : (
          <pre className="artifact-code-view">{artifact.content}</pre>
        )}
      </div>

      {/* Security Footer Notice */}
      <div className="artifact-security-notice">
        <ShieldCheck size={13} style={{ color: 'var(--success)' }} />
        <span>Sandboxed isolation active. No host session or credential access permitted.</span>
      </div>
    </aside>
  );
};
