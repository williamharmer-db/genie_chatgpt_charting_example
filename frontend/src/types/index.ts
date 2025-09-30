// Type definitions for the Genie to Chart POC

// ===== CONVERSATIONAL INTERFACE TYPES =====

// Message types for conversational interface
export interface Message {
  id: string;
  conversation_id: string;
  type: 'user' | 'assistant_text' | 'assistant_chart' | 'assistant_error';
  content: string;
  timestamp: string;
  metadata?: {
    chart_config?: any;
    ai_summary?: string;
    chart_reasoning?: string;
    chart_type?: string;
    sql_query?: string;
    data?: any[];
    columns?: string[];
    response_type?: 'chart' | 'text';
    is_mock_data?: boolean;
    error?: string;
  };
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  message_count: number;
  is_active: boolean;
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  is_active: boolean;
}

// API Response types for conversations
export interface ConversationResponse {
  success: boolean;
  conversation_id: string;
  user_message_id: string;
  assistant_message_id: string;
  response_type: 'chart' | 'text';
  content: string;
  chart_config?: any;
  ai_summary?: string;
  chart_reasoning?: string;
  chart_type?: string;
  sql_query?: string;
  data?: any[];
  columns?: string[];
  is_mock_data?: boolean;
}

// ===== LEGACY TYPES (for backwards compatibility) =====

// Base interface for all Genie responses
export interface BaseGenieResponse {
  success: boolean;
  question: string;
  response_type: 'chart' | 'text';
}

// Chart response interface
export interface GenieChartResult extends BaseGenieResponse {
  response_type: 'chart';
  sql_query: string;
  data_summary: {
    columns: string[];
    row_count: number;
    sample_data: any[][];
    ai_summary: string; // AI-generated summary of the data insights
  };
  chart_spec: {
    chart_type: string;
    title: string;
    reasoning: string;
    library: string;
  };
  chart_config: any; // Chart.js configuration
  is_mock_data?: boolean; // Whether this is mock/demo data
}

// Text response interface
export interface GenieTextResult extends BaseGenieResponse {
  response_type: 'text';
  text_response: string;
  sql_query?: string; // Optional SQL query if available
}

// Union type for all possible responses
export type GenieQueryResult = GenieChartResult | GenieTextResult;

export interface ApiError {
  error: string;
  success: false;
}

// ===== COMPONENT PROP TYPES =====

export interface ConversationListProps {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (conversationId: string) => void;
  loading?: boolean;
}

export interface ChatMessageProps {
  message: Message;
  isLatest?: boolean;
}

export interface ChatInterfaceProps {
  conversation: Conversation | null;
  onSendMessage: (message: string) => void;
  loading: boolean;
}

// Removed unused component prop types - functionality moved to ChatMessage component