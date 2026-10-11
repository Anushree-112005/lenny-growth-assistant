import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Loader2 } from 'lucide-react';

interface ChatComposerProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="composer-container">
      <form className="composer-box" onSubmit={handleSubmit}>
        <textarea
          ref={textareaRef}
          className="composer-textarea"
          placeholder="Ask anything grounded in Lenny's Podcast and Newsletter transcripts..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={1}
        />
        <div className="composer-footer">
          <span className="composer-shortcuts">
            Press <strong>Enter</strong> to submit, <strong>Shift + Enter</strong> for newline
          </span>
          <button
            type="submit"
            className="btn-send"
            disabled={!input.trim() || isLoading}
            title="Send question"
          >
            {isLoading ? (
              <Loader2 size={14} className="spinner" />
            ) : (
              <>
                <span>Ask</span>
                <ArrowUp size={14} />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
