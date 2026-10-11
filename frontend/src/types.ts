export interface Citation {
  id: string;
  chunk_id: string;
  document_id: string;
  title: string;
  url?: string | null;
  excerpt: string;
  relevance_score: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  provider?: string | null;
  model?: string | null;
  abstained?: boolean;
  created_at: string;
  citations: Citation[];
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface ConversationDetail extends ConversationSummary {
  messages: Message[];
  artifacts: ArtifactSummary[];
}

export interface ArtifactSummary {
  id: string;
  title: string;
  artifact_type: string;
  created_at: string;
  is_evidence_grounded: boolean;
}

export interface ArtifactDetail extends ArtifactSummary {
  conversation_id?: string | null;
  content: string;
  metadata?: Record<string, any>;
}

export interface ProviderHealth {
  status: 'available' | 'unavailable' | 'not_configured' | 'error';
  model?: string;
  error?: string;
  message?: string;
  installed_models?: string[];
}

export interface ProviderInfo {
  id: string;
  name: string;
  model: string;
  is_default: boolean;
  health: ProviderHealth;
}

export interface SourceDocument {
  id: string;
  title: string;
  source_type: string;
  url?: string | null;
  author: string;
  chunks_count: number;
  ingested_at: string;
}

export interface Ship30Response {
  title: string;
  essay: string;
  word_count: number;
  abstained: boolean;
  citations: Citation[];
  artifact_id?: string | null;
  provider: string;
  model: string;
}
