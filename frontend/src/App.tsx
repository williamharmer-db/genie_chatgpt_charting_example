import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ConversationList from './components/ConversationList';
import ChatInterface from './components/ChatInterface';
import { Conversation, ConversationSummary, Message } from './types';
import './App.css';

// Configure axios to include credentials for session management
axios.defaults.withCredentials = true;

const App: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [conversationLoadingStates, setConversationLoadingStates] = useState<Record<string, boolean>>({});
  const [conversationsLoading, setConversationsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load conversations on app start
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setConversationsLoading(true);
      const response = await axios.get('/api/conversations');
      if (response.data.success) {
        setConversations(response.data.conversations);
      }
    } catch (err: any) {
      console.error('Failed to load conversations:', err);
    } finally {
      setConversationsLoading(false);
    }
  };

  const loadConversation = async (conversationId: string) => {
    try {
      const response = await axios.get(`/api/conversations/${conversationId}`);
      if (response.data.success) {
        setActiveConversation(response.data.conversation);
        setError(null);
        
        // If we got a new conversation ID (due to recovery), update the conversations list
        if (response.data.new_conversation_id) {
          await loadConversations();
        }
      }
    } catch (err: any) {
      setError('Failed to load conversation');
      console.error('Failed to load conversation:', err);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await axios.post('/api/conversations', {});
      if (response.data.success) {
        const newConversationId = response.data.conversation_id;
        
        // Reload conversations list
        await loadConversations();
        
        // Load the new conversation
        await loadConversation(newConversationId);
      }
    } catch (err: any) {
      setError('Failed to create new conversation');
      console.error('Failed to create conversation:', err);
    }
  };

  const handleSelectConversation = (conversationId: string) => {
    if (conversationId !== activeConversation?.id) {
      loadConversation(conversationId);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    try {
      const response = await axios.delete(`/api/conversations/${conversationId}`);
      if (response.data.success) {
        // Remove from conversations list
        setConversations(prev => prev.filter(conv => conv.id !== conversationId));
        
        // Clean up loading state for this conversation
        setConversationLoadingStates(prev => {
          const newState = { ...prev };
          delete newState[conversationId];
          return newState;
        });
        
        // If this was the active conversation, clear it
        if (activeConversation?.id === conversationId) {
          setActiveConversation(null);
        }
      }
    } catch (err: any) {
      setError('Failed to delete conversation');
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!activeConversation) {
      setError('No active conversation');
      return;
    }

    const conversationId = activeConversation.id;

    // Create user message for immediate display and error cleanup
    const userMessage: Message = {
      id: `temp-${Date.now()}`, // Temporary ID
      conversation_id: conversationId,
      type: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      metadata: undefined
    };

    try {
      setError(null);

      // Immediately add user message to the conversation UI
      setActiveConversation(prev => {
        if (prev && prev.id === conversationId) {
          return {
            ...prev,
            messages: [...prev.messages, userMessage],
            updated_at: userMessage.timestamp
          };
        }
        return prev;
      });

      // Set loading state AFTER showing the user message
      setConversationLoadingStates(prev => ({ ...prev, [conversationId]: true }));

      // Submit message to queue
      const response = await axios.post(
        `/api/conversations/${conversationId}/messages`,
        { message }
      );

      if (response.data.success) {
        const messageId = response.data.message_id;
        
        // Poll for message completion
        await pollForMessageCompletion(messageId, conversationId);
      } else {
        setError('Failed to queue message');
        // Remove the temporary user message on error
        setActiveConversation(prev => {
          if (prev && prev.id === conversationId) {
            return {
              ...prev,
              messages: prev.messages.filter(msg => msg.id !== userMessage.id)
            };
          }
          return prev;
        });
      }
    } catch (err: any) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.message) {
        setError(`Network error: ${err.message}`);
      } else {
        setError('An unexpected error occurred');
      }
      console.error('Failed to send message:', err);
      
      // Remove the temporary user message on error
      setActiveConversation(prev => {
        if (prev && prev.id === conversationId) {
          return {
            ...prev,
            messages: prev.messages.filter(msg => msg.id !== userMessage.id)
          };
        }
        return prev;
      });
      
      // Clear loading state on error
      setConversationLoadingStates(prev => ({ ...prev, [conversationId]: false }));
    }
  };

  const pollForMessageCompletion = async (messageId: string, conversationId: string) => {
    const maxAttempts = 60; // Poll for up to 60 seconds
    const pollInterval = 1000; // Poll every 1 second
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const statusResponse = await axios.get(`/api/messages/${messageId}/status`);
        
        if (statusResponse.data.success) {
          const status = statusResponse.data.status;
          
          if (status === 'completed') {
            // Message completed successfully
            await loadConversation(conversationId);
            await loadConversations();
            setConversationLoadingStates(prev => ({ ...prev, [conversationId]: false }));
            return;
          } else if (status === 'failed') {
            // Message processing failed
            const error = statusResponse.data.error || 'Message processing failed';
            setError(error);
            setConversationLoadingStates(prev => ({ ...prev, [conversationId]: false }));
            return;
          }
          // If status is 'queued' or 'processing', continue polling
        }
        
        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, pollInterval));
      } catch (err) {
        console.error('Error polling message status:', err);
        // Continue polling on error
        await new Promise(resolve => setTimeout(resolve, pollInterval));
      }
    }
    
    // Timeout reached
    setError('Message processing timed out. Please try again.');
    setConversationLoadingStates(prev => ({ ...prev, [conversationId]: false }));
  };

  return (
    <div className="app">
      {/* Sidebar with conversation list */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>Genie Chat</h1>
          <p>AI-powered data conversations</p>
        </div>
        
        <div className="sidebar-content">
          <ConversationList
            conversations={conversations}
            activeConversationId={activeConversation?.id || null}
            onSelectConversation={handleSelectConversation}
            onNewConversation={createNewConversation}
            onDeleteConversation={handleDeleteConversation}
            loading={conversationsLoading}
          />

          <div className="workflow-info">
            <h4>⚡ How it works</h4>
            <div className="workflow-steps">
              <div className="workflow-step">
                <span className="step-number">1</span>
                <div className="step-content">
                  <strong>Natural Language</strong>
                  <p>Ask questions in plain English</p>
                </div>
              </div>
              <div className="workflow-step">
                <span className="step-number">2</span>
                <div className="step-content">
                  <strong>Databricks Genie</strong>
                  <p>Converts to SQL and retrieves data</p>
                </div>
              </div>
              <div className="workflow-step">
                <span className="step-number">3</span>
                <div className="step-content">
                  <strong>AI Analysis</strong>
                  <p>GPT-5 provides insights and visualizations</p>
                </div>
              </div>
            </div>
          </div>

          <div className="tech-stack">
            <h4>🛠️ Tech Stack</h4>
            <div className="tech-badges">
              <span className="tech-badge">React</span>
              <span className="tech-badge">TypeScript</span>
              <span className="tech-badge">react-chartjs-2</span>
              <span className="tech-badge">Databricks Genie</span>
              <span className="tech-badge">Azure OpenAI</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main chat interface */}
      <main className="main-content">
        {error && (
          <div className="global-error">
            <div className="error-content">
              <span className="error-icon">⚠️</span>
              <span className="error-message">{error}</span>
              <button 
                className="error-dismiss"
                onClick={() => setError(null)}
              >
                ×
              </button>
            </div>
          </div>
        )}
        
        <ChatInterface
          conversation={activeConversation}
          onSendMessage={handleSendMessage}
          loading={activeConversation ? conversationLoadingStates[activeConversation.id] || false : false}
        />
      </main>
    </div>
  );
};

export default App;