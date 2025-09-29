import React, { useState } from 'react';
import { ChatMessageProps } from '../types';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import './ChatMessage.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isLatest = false }) => {
  const [showDetails, setShowDetails] = useState(false);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffMinutes = Math.floor(diffTime / (1000 * 60));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffMinutes < 1) {
      return 'Just now';
    } else if (diffMinutes < 60) {
      return `${diffMinutes}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };

  const renderChart = (chartConfig: any) => {
    const chartType = chartConfig?.type || 'bar';
    
    try {
      switch (chartType) {
        case 'line':
          return <Line data={chartConfig.data} options={chartConfig.options} />;
        case 'pie':
          return <Pie data={chartConfig.data} options={chartConfig.options} />;
        case 'bar':
        default:
          return <Bar data={chartConfig.data} options={chartConfig.options} />;
      }
    } catch (error) {
      console.error('Chart rendering error:', error);
      return (
        <div className="chart-error">
          <p>Unable to render chart</p>
          <small>Chart configuration error</small>
        </div>
      );
    }
  };

  const renderUserMessage = () => (
    <div className="chat-message user-message">
      <div className="message-content">
        <div className="message-text">{message.content}</div>
        <div className="message-timestamp">{formatTimestamp(message.timestamp)}</div>
      </div>
      <div className="message-avatar user-avatar">You</div>
    </div>
  );

  const renderAssistantTextMessage = () => (
    <div className="chat-message assistant-message">
      <div className="message-avatar assistant-avatar">🤖</div>
      <div className="message-content">
        <div className="message-text">
          {message.content}
        </div>
        
        {message.metadata?.sql_query && (
          <div className="sql-query-section">
            <details>
              <summary>View SQL Query</summary>
              <pre className="sql-code">{message.metadata.sql_query}</pre>
            </details>
          </div>
        )}
        
        <div className="message-timestamp">{formatTimestamp(message.timestamp)}</div>
      </div>
    </div>
  );

  const renderAssistantChartMessage = () => (
    <div className="chat-message assistant-message chart-message">
      <div className="message-avatar assistant-avatar">📊</div>
      <div className="message-content">
        
        {/* AI Summary */}
        <div className="ai-summary-section">
          <h4>Data Insights</h4>
          <div className="ai-summary-text">{message.content}</div>
        </div>

        {/* Chart */}
        {message.metadata?.chart_config && (
          <div className="chart-section">
            <div className="chart-header">
              <h4>Visualization</h4>
              {(message.metadata?.sql_query || message.metadata?.data || message.metadata?.chart_reasoning) && (
                <button 
                  className="details-toggle-btn"
                  onClick={() => setShowDetails(!showDetails)}
                  title="Show technical details"
                >
                  🧠
                </button>
              )}
            </div>
            
            <div className="chart-container">
              {message.metadata.is_mock_data && (
                <div className="mock-data-badge">Demo Data</div>
              )}
              {renderChart(message.metadata.chart_config)}
            </div>

            {/* Collapsible Technical Details */}
            {showDetails && (
              <div className="technical-details">
                <div className="details-header">
                  <h5>Technical Details</h5>
                </div>

                {message.metadata?.sql_query && (
                  <div className="detail-section">
                    <h6>SQL Query</h6>
                    <div className="sql-card">
                      <pre className="sql-code">{message.metadata.sql_query}</pre>
                    </div>
                  </div>
                )}

                {message.metadata?.data && message.metadata?.columns && (
                  <div className="detail-section">
                    <h6>Data Sample</h6>
                    <div className="data-card">
                      <div className="data-meta">
                        {message.metadata.data.length} rows × {message.metadata.columns.length} columns
                      </div>
                      <div className="data-table-container">
                        <table className="data-table">
                          <thead>
                            <tr>
                              {message.metadata.columns.map((col: string, idx: number) => (
                                <th key={idx}>{col}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {message.metadata.data.slice(0, 5).map((row: any[], rowIdx: number) => (
                              <tr key={rowIdx}>
                                {row.map((cell: any, cellIdx: number) => (
                                  <td key={cellIdx}>{String(cell)}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}

                {message.metadata?.chart_reasoning && (
                  <div className="detail-section">
                    <h6>Chart Selection Reasoning</h6>
                    <div className="reasoning-card">
                      <div className="chart-meta">
                        Chart Type: {message.metadata.chart_type} | Library: react-chartjs-2
                      </div>
                      <div className="reasoning-text">{message.metadata.chart_reasoning}</div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        
        <div className="message-timestamp">{formatTimestamp(message.timestamp)}</div>
      </div>
    </div>
  );

  const renderErrorMessage = () => (
    <div className="chat-message assistant-message error-message">
      <div className="message-avatar error-avatar">⚠️</div>
      <div className="message-content">
        <div className="error-content">
          <h4>Error</h4>
          <div className="message-text">{message.content}</div>
        </div>
        <div className="message-timestamp">{formatTimestamp(message.timestamp)}</div>
      </div>
    </div>
  );

  switch (message.type) {
    case 'user':
      return renderUserMessage();
    case 'assistant_text':
      return renderAssistantTextMessage();
    case 'assistant_chart':
      return renderAssistantChartMessage();
    case 'assistant_error':
      return renderErrorMessage();
    default:
      return null;
  }
};

export default ChatMessage;

