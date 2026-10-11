import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ChatMessage } from './components/ChatMessage';
import { ChatComposer } from './components/ChatComposer';
import { ArtifactViewer } from './components/ArtifactViewer';
import { Ship30Modal } from './components/Ship30Modal';
import { SourcesModal } from './components/SourcesModal';
import { Sparkles, ArrowRight, Zap, Target, TrendingUp, Layers } from 'lucide-react';
import {
  ConversationSummary,
  ConversationDetail,
  Message,
  ProviderInfo,
  ArtifactDetail,
  SourceDocument,
} from './types';
import {
  fetchProviders,
  fetchConversations,
  fetchConversation,
  createConversation,
  deleteConversation,
  sendChatMessage,
  generateShip30Essay,
  createArtifact,
  fetchArtifact,
  fetchSources,
} from './api';

export const App: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [activeConversation, setActiveConversation] = useState<ConversationDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('ollama');
  const [sources, setSources] = useState<SourceDocument[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Deliverables & Modals
  const [activeArtifact, setActiveArtifact] = useState<ArtifactDetail | null>(null);
  const [isArtifactOpen, setIsArtifactOpen] = useState<boolean>(false);
  const [isShip30Open, setIsShip30Open] = useState<boolean>(false);
  const [isSourcesOpen, setIsSourcesOpen] = useState<boolean>(false);

  // Initial Data Load
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [provs, convs, srcs] = await Promise.all([
        fetchProviders(),
        fetchConversations(),
        fetchSources(),
      ]);
      setProviders(provs);
      setSources(srcs);
      setConversations(convs);

      // Select default provider from server
      const defaultProv = provs.find((p) => p.is_default);
      if (defaultProv) setSelectedProvider(defaultProv.id);

      // Select first conversation if exists, or start new
      if (convs.length > 0) {
        selectConversation(convs[0].id);
      }
    } catch (err) {
      console.error('Failed to load initial workspace data:', err);
    }
  };

  const selectConversation = async (id: string) => {
    setActiveId(id);
    try {
      const detail = await fetchConversation(id);
      setActiveConversation(detail);
      setMessages(detail.messages || []);

      // If conversation has artifacts, load latest
      if (detail.artifacts && detail.artifacts.length > 0) {
        const latestArt = await fetchArtifact(detail.artifacts[detail.artifacts.length - 1].id);
        setActiveArtifact(latestArt);
      }
    } catch (err) {
      console.error('Failed to load conversation details:', err);
    }
  };

  const handleNewChat = async () => {
    try {
      const newConv = await createConversation('New Conversation');
      setConversations([newConv, ...conversations]);
      setActiveId(newConv.id);
      setActiveConversation({ ...newConv, messages: [], artifacts: [] });
      setMessages([]);
      setActiveArtifact(null);
      setIsArtifactOpen(false);
    } catch (err) {
      console.error('Failed to create new conversation:', err);
    }
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteConversation(id);
      const remaining = conversations.filter((c) => c.id !== id);
      setConversations(remaining);
      if (activeId === id) {
        if (remaining.length > 0) {
          selectConversation(remaining[0].id);
        } else {
          setActiveId(null);
          setActiveConversation(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    let targetConvId = activeId;
    if (!targetConvId) {
      const newConv = await createConversation(text.slice(0, 30));
      targetConvId = newConv.id;
      setConversations([newConv, ...conversations]);
      setActiveId(targetConvId);
    }

    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
      citations: [],
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const chatRes = await sendChatMessage(text, targetConvId, selectedProvider);
      const assistantMsg: Message = {
        id: chatRes.message_id,
        role: 'assistant',
        content: chatRes.content,
        provider: chatRes.provider,
        model: chatRes.model,
        abstained: chatRes.abstained,
        created_at: new Date().toISOString(),
        citations: chatRes.citations || [],
      };
      setMessages((prev) => [...prev, assistantMsg]);

      const updatedConvs = await fetchConversations();
      setConversations(updatedConvs);
    } catch (err: any) {
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `**Error:** ${err.message || 'Failed to process response from model provider.'}`,
        created_at: new Date().toISOString(),
        citations: [],
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateArtifact = async (prompt: string, type: string) => {
    setIsLoading(true);
    try {
      const art = await createArtifact({
        title: `Deliverable: ${prompt.slice(0, 35)}...`,
        artifact_type: type,
        prompt: prompt,
        conversation_id: activeId || undefined,
        provider: selectedProvider,
      });
      setActiveArtifact(art);
      setIsArtifactOpen(true);
    } catch (err: any) {
      alert(`Artifact generation failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShip30Generate = async (topic: string) => {
    const res = await generateShip30Essay(topic, activeId || undefined, selectedProvider);
    if (res.artifact_id) {
      const art = await fetchArtifact(res.artifact_id);
      setActiveArtifact(art);
    }
    if (activeId) {
      selectConversation(activeId);
    }
    return res;
  };

  const handleOpenArtifactById = async (artId: string) => {
    try {
      const art = await fetchArtifact(artId);
      setActiveArtifact(art);
      setIsArtifactOpen(true);
    } catch (err) {
      console.error('Failed to open artifact:', err);
    }
  };

  const heroSuggestions = [
    {
      tag: 'B2B Product-Led Growth',
      icon: <Zap size={14} style={{ color: 'var(--primary)' }} />,
      query: 'How does Elena Verna explain B2B PLG vs sales-assisted models?',
      desc: 'Understand end-user adoption engines and monetization vectors.'
    },
    {
      tag: 'The Four Fits Framework',
      icon: <Layers size={14} style={{ color: 'var(--primary)' }} />,
      query: 'What are the Four Fits according to Brian Balfour?',
      desc: 'Market-Product, Product-Channel, Channel-Model, Model-Market.'
    },
    {
      tag: 'Diagnosing Retention Curves',
      icon: <TrendingUp size={14} style={{ color: 'var(--primary)' }} />,
      query: 'Why are retention curves the true test of Product-Market Fit according to Casey Winters?',
      desc: 'Learn why flattening parallel to baseline indicates enduring PMF.'
    },
    {
      tag: 'SaaS Pricing & Packaging',
      icon: <Target size={14} style={{ color: 'var(--primary)' }} />,
      query: 'What are the core pricing models and value metric selection rules in SaaS?',
      desc: 'Discover why value metric pivots unlock compounding expansion revenue.'
    },
  ];

  return (
    <div className="app-container">
      {/* Left Sidebar */}
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNewChat={handleNewChat}
        onDelete={handleDeleteConversation}
        onOpenSources={() => setIsSourcesOpen(true)}
        sourcesCount={sources.length}
      />

      {/* Main Content Area */}
      <div className="main-content">
        <Header
          conversationTitle={activeConversation?.title}
          providers={providers}
          selectedProvider={selectedProvider}
          onSelectProvider={setSelectedProvider}
          onOpenShip30={() => setIsShip30Open(true)}
          onToggleArtifacts={() => setIsArtifactOpen(!isArtifactOpen)}
          isArtifactOpen={isArtifactOpen}
          artifactsCount={activeConversation?.artifacts?.length || 0}
        />

        {/* Chat Thread */}
        <div className="chat-thread-container">
          <div className="chat-thread">
            {messages.length === 0 ? (
              <div className="welcome-container">
                <div className="welcome-badge">
                  <Sparkles size={12} />
                  <span>Evidence-Grounded Intelligence</span>
                </div>
                <h1 className="welcome-title">The Lenny Growth Assistant</h1>
                <p className="welcome-desc">
                  An executive-grade research partner querying Lenny Rachitsky's podcast
                  transcripts and growth playbooks. Grounded answers, verifiable citations, and zero hallucinations.
                </p>

                <div className="welcome-suggestions">
                  {heroSuggestions.map((s, idx) => (
                    <div
                      key={idx}
                      className="suggestion-card"
                      onClick={() => handleSendMessage(s.query)}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          {s.icon}
                          <span className="suggestion-tag">{s.tag}</span>
                        </div>
                        <ArrowRight size={13} style={{ color: 'var(--text-muted)' }} />
                      </div>
                      <div className="suggestion-title">{s.query}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>{s.desc}</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m) => (
                <ChatMessage
                  key={m.id}
                  message={m}
                  onGenerateArtifact={handleGenerateArtifact}
                  onDraftShip30={() => setIsShip30Open(true)}
                  onSelectSuggestion={handleSendMessage}
                />
              ))
            )}
          </div>
        </div>

        {/* Composer */}
        <ChatComposer onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>

      {/* Right Artifact Viewer Panel */}
      {isArtifactOpen && (
        <ArtifactViewer
          artifact={activeArtifact}
          onClose={() => setIsArtifactOpen(false)}
        />
      )}

      {/* Modals */}
      <Ship30Modal
        isOpen={isShip30Open}
        onClose={() => setIsShip30Open(false)}
        onGenerate={handleShip30Generate}
        onOpenArtifact={handleOpenArtifactById}
      />

      <SourcesModal
        isOpen={isSourcesOpen}
        onClose={() => setIsSourcesOpen(false)}
        sources={sources}
      />
    </div>
  );
};

export default App;
