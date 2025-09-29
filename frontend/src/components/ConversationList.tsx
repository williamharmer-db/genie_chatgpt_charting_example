import React from 'react';
import { ConversationListProps } from '../types';
import './ConversationList.css';

const ConversationList: React.FC<ConversationListProps> = ({ 
  conversations, 
  activeConversationId, 
  onSelectConversation, 
  onNewConversation, 
  onDeleteConversation,
  loading = false
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
      return 'Today';
    } else if (diffDays === 2) {
      return 'Yesterday';
    } else if (diffDays <= 7) {
      return `${diffDays - 1} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const truncateTitle = (title: string, maxLength: number = 40) => {
    return title.length > maxLength ? title.substring(0, maxLength) + '...' : title;
  };

  const handleDeleteClick = (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation(); // Prevent selecting the conversation
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      onDeleteConversation(conversationId);
    }
  };

  return (
    <div className="conversation-list">
      <div className="conversation-list-header">
        <h3>Conversations</h3>
        <button 
          className="new-conversation-btn"
          onClick={onNewConversation}
          disabled={loading}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Chat
        </button>
      </div>

      <div className="conversation-list-content">
        {loading && conversations.length === 0 ? (
          <div className="loading-conversations">
            <div className="loading-spinner"></div>
            <span>Loading conversations...</span>
          </div>
        ) : conversations.length === 0 ? (
          <div className="empty-conversations">
            <div className="empty-icon">💬</div>
            <p>No conversations yet</p>
            <p className="empty-subtitle">Start a new conversation to begin exploring your data</p>
          </div>
        ) : (
          <div className="conversations">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`conversation-item ${
                  activeConversationId === conversation.id ? 'active' : ''
                }`}
                onClick={() => onSelectConversation(conversation.id)}
              >
                <div className="conversation-content">
                  <div className="conversation-title">
                    {truncateTitle(conversation.title)}
                  </div>
                  <div className="conversation-meta">
                    <span className="conversation-date">
                      {formatDate(conversation.updated_at)}
                    </span>
                    <span className="conversation-messages">
                      {conversation.message_count} messages
                    </span>
                  </div>
                </div>
                <button
                  className="delete-conversation-btn"
                  onClick={(e) => handleDeleteClick(e, conversation.id)}
                  title="Delete conversation"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3,6 5,6 21,6"></polyline>
                    <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationList;

