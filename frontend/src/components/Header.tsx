import React from 'react';
import { PenTool, LayoutTemplate, Cpu } from 'lucide-react';
import { ProviderInfo } from '../types';

interface HeaderProps {
  conversationTitle?: string;
  providers: ProviderInfo[];
  selectedProvider: string;
  onSelectProvider: (provider: string) => void;
  onOpenShip30: () => void;
  onToggleArtifacts: () => void;
  isArtifactOpen: boolean;
  artifactsCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  conversationTitle,
  providers,
  selectedProvider,
  onSelectProvider,
  onOpenShip30,
  onToggleArtifacts,
  isArtifactOpen,
  artifactsCount,
}) => {
  const currentProvider = providers.find((p) => p.id === selectedProvider);
  const healthStatus = currentProvider?.health?.status || 'available';

  return (
    <header className="top-header">
      <div className="header-left">
        <h2 className="header-title">{conversationTitle || 'Editorial Workspace'}</h2>
      </div>

      <div className="header-actions">
        {/* Model Provider Selector */}
        <div className="provider-select-wrapper" title={`Active: ${currentProvider?.model || selectedProvider}`}>
          <span className={`status-dot ${healthStatus}`} />
          <Cpu size={13} style={{ color: 'var(--text-muted)' }} />
          <select
            className="provider-select"
            value={selectedProvider}
            onChange={(e) => onSelectProvider(e.target.value)}
          >
            {providers.map((p) => {
              const statusTag = p.health?.status === 'available' ? '' : ` (${p.health?.status || 'offline'})`;
              return (
                <option key={p.id} value={p.id}>
                  {p.name}: {p.model}{statusTag}
                </option>
              );
            })}
          </select>
        </div>

        {/* Ship 30 for 30 Skill Trigger */}
        <button className="btn-header-action" onClick={onOpenShip30} title="Generate Ship 30 for 30 Essay">
          <PenTool size={13} />
          <span>Ship 30 Essay</span>
        </button>

        {/* Artifact Viewer Toggle */}
        <button
          className={`btn-header-action ${isArtifactOpen ? 'active' : ''}`}
          onClick={onToggleArtifacts}
          title="Toggle Artifact Viewer"
        >
          <LayoutTemplate size={13} />
          <span>Artifacts {artifactsCount > 0 ? `(${artifactsCount})` : ''}</span>
        </button>
      </div>
    </header>
  );
};
