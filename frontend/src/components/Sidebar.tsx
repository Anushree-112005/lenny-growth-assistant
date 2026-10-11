import React from 'react';
import { Plus, MessageSquare, Trash2, Database } from 'lucide-react';
import { ConversationSummary } from '../types';

interface SidebarProps {
  conversations: ConversationSummary[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onDelete: (id: string, e: React.MouseEvent) => void;
  onOpenSources: () => void;
  sourcesCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeId,
  onSelect,
  onNewChat,
  onDelete,
  onOpenSources,
  sourcesCount,
}) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-badge">
          <div className="brand-icon">L</div>
          <div>
            <div className="brand-title">Lenny Growth</div>
            <div className="brand-subtitle">Assistant Workspace</div>
          </div>
        </div>

        <button className="btn-new-chat" onClick={onNewChat}>
          <Plus size={16} />
          <span>New Conversation</span>
        </button>
      </div>

      <div className="conversations-list">
        <div className="section-label">Recent Sessions</div>
        {conversations.length === 0 ? (
          <div style={{ padding: '12px 10px', fontSize: '13px', color: 'var(--text-muted)' }}>
            No sessions yet. Start a new conversation!
          </div>
        ) : (
          conversations.map((c) => (
            <div
              key={c.id}
              className={`conversation-item ${activeId === c.id ? 'active' : ''}`}
              onClick={() => onSelect(c.id)}
            >
              <MessageSquare size={14} style={{ marginRight: 8, flexShrink: 0 }} />
              <span className="conversation-title">{c.title || 'Conversation'}</span>
              <button
                className="btn-delete-conv"
                title="Delete session"
                onClick={(e) => onDelete(c.id, e)}
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <button className="btn-sources" onClick={onOpenSources}>
          <Database size={14} />
          <span>Ingested Sources ({sourcesCount})</span>
        </button>
      </div>
    </aside>
  );
};
