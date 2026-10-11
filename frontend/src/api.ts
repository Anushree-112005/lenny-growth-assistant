import {
  ConversationSummary,
  ConversationDetail,
  ProviderInfo,
  ArtifactDetail,
  SourceDocument,
  Ship30Response,
} from './types';

const BASE_URL = '';

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchProviders(): Promise<ProviderInfo[]> {
  const res = await fetch(`${BASE_URL}/api/providers`);
  if (!res.ok) throw new Error('Failed to fetch providers');
  return res.json();
}

export async function fetchConversations(): Promise<ConversationSummary[]> {
  const res = await fetch(`${BASE_URL}/api/conversations`);
  if (!res.ok) throw new Error('Failed to fetch conversations');
  return res.json();
}

export async function createConversation(title?: string): Promise<ConversationSummary> {
  const res = await fetch(`${BASE_URL}/api/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error('Failed to create conversation');
  return res.json();
}

export async function fetchConversation(id: string): Promise<ConversationDetail> {
  const res = await fetch(`${BASE_URL}/api/conversations/${id}`);
  if (!res.ok) throw new Error('Failed to fetch conversation');
  return res.json();
}

export async function deleteConversation(id: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/conversations/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete conversation');
}

export async function sendChatMessage(
  message: string,
  conversationId: string,
  provider?: string
): Promise<{
  conversation_id: string;
  message_id: string;
  role: string;
  content: string;
  provider: string;
  model: string;
  abstained: boolean;
  citations: any[];
}> {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      provider,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Chat request failed' }));
    throw new Error(err.detail || 'Chat request failed');
  }
  return res.json();
}

export async function generateShip30Essay(
  topic: string,
  conversationId?: string,
  provider?: string
): Promise<Ship30Response> {
  const res = await fetch(`${BASE_URL}/api/skills/ship-30-for-30`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic,
      conversation_id: conversationId,
      provider,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Ship 30 generation failed' }));
    throw new Error(err.detail || 'Ship 30 generation failed');
  }
  return res.json();
}

export async function createArtifact(data: {
  title: string;
  artifact_type: string;
  content?: string;
  prompt?: string;
  conversation_id?: string;
  provider?: string;
}): Promise<ArtifactDetail> {
  const res = await fetch(`${BASE_URL}/api/artifacts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Artifact creation failed' }));
    throw new Error(err.detail || 'Artifact creation failed');
  }
  return res.json();
}

export async function fetchArtifact(id: string): Promise<ArtifactDetail> {
  const res = await fetch(`${BASE_URL}/api/artifacts/${id}`);
  if (!res.ok) throw new Error('Failed to fetch artifact');
  return res.json();
}

export async function fetchSources(): Promise<SourceDocument[]> {
  const res = await fetch(`${BASE_URL}/api/sources`);
  if (!res.ok) throw new Error('Failed to fetch sources');
  return res.json();
}
