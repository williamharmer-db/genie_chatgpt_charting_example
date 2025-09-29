import React, { useState, useRef, useEffect } from 'react';
import { ChatInterfaceProps } from '../types';
import ChatMessage from './ChatMessage';
import './ChatInterface.css';

const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  conversation, 
  onSendMessage, 
  loading 
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && !loading) {
      onSendMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const adjustTextareaHeight = () => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputMessage]);

  if (!conversation) {
    return (
      <div className="chat-interface">
        <div className="chat-empty-state">
          <div className="empty-state-content">
            <div className="empty-state-icon">💬</div>
            <h2>Welcome to Genie Chat</h2>
            <p>Start a conversation to explore your data with natural language queries.</p>
            <div className="empty-state-features">
              <div className="feature-item">
                <span className="feature-icon">🔍</span>
                <span>Ask questions in plain English</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📊</span>
                <span>Get intelligent visualizations</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🧠</span>
                <span>Receive AI-powered insights</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>{conversation.title}</h2>
        <div className="chat-info">
          {conversation.messages.length} messages
        </div>
      </div>

      <div className="chat-messages">
        {conversation.messages.length === 0 ? (
          <div className="conversation-empty-state">
            <div className="empty-conversation-content">
              <div className="empty-conversation-icon">🚀</div>
              <h3>Ready to explore your data?</h3>
              <p>Ask me anything about your data. I'll help you understand it with insights and visualizations.</p>
              
              <div className="example-prompts">
                <h4>Try asking:</h4>
                <div className="prompt-examples">
                  <button 
                    className="example-prompt"
                    onClick={() => setInputMessage("What are the top 5 products by sales?")}
                    disabled={loading}
                  >
                    "What are the top 5 products by sales?"
                  </button>
                  <button 
                    className="example-prompt"
                    onClick={() => setInputMessage("Show me revenue trends over time")}
                    disabled={loading}
                  >
                    "Show me revenue trends over time"
                  </button>
                  <button 
                    className="example-prompt"
                    onClick={() => setInputMessage("Which regions have the highest customer counts?")}
                    disabled={loading}
                  >
                    "Which regions have the highest customer counts?"
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {conversation.messages.map((message, index) => (
              <ChatMessage 
                key={message.id} 
                message={message} 
                isLatest={index === conversation.messages.length - 1}
              />
            ))}
            
            {loading && (
              <div className="typing-indicator">
                <div className="message-avatar assistant-avatar">🤖</div>
                <div className="typing-content">
                  <div className="typing-animation">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                  <span className="typing-text">Genie is thinking...</span>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <form onSubmit={handleSubmit} className="chat-input-form">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={loading ? "Genie is processing..." : "Ask me anything about your data..."}
              disabled={loading}
              className="chat-input"
              rows={1}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={loading || !inputMessage.trim()}
            >
              {loading ? (
                <div className="button-spinner"></div>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              )}
            </button>
          </div>
          <div className="input-hint">
            Press Enter to send • Shift+Enter for new line
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;

