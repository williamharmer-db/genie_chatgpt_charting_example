import React from 'react';
import './ErrorDisplay.css';

interface ErrorDisplayProps {
  error: string;
  onRetry?: () => void;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry }) => {
  const getErrorIcon = (error: string) => {
    if (error.toLowerCase().includes('network')) return '🌐';
    if (error.toLowerCase().includes('configuration')) return '⚙️';
    if (error.toLowerCase().includes('permission')) return '🔐';
    if (error.toLowerCase().includes('rate limit')) return '⏱️';
    return '❌';
  };

  const getErrorSuggestion = (error: string) => {
    if (error.toLowerCase().includes('network')) {
      return 'Please check your internet connection and try again.';
    }
    if (error.toLowerCase().includes('configuration')) {
      return 'Please check your environment configuration (.env file).';
    }
    if (error.toLowerCase().includes('permission')) {
      return 'Please check your Databricks and OpenAI API credentials.';
    }
    if (error.toLowerCase().includes('rate limit')) {
      return 'Please wait a moment before trying again.';
    }
    if (error.toLowerCase().includes('no data')) {
      return 'Try rephrasing your question or check if the data exists.';
    }
    return 'Please try again or contact support if the issue persists.';
  };

  return (
    <div className="error-container">
      <div className="error-content">
        <div className="error-icon">
          {getErrorIcon(error)}
        </div>
        <h3 className="error-title">Something went wrong</h3>
        <p className="error-message">{error}</p>
        <p className="error-suggestion">{getErrorSuggestion(error)}</p>
        
        {onRetry && (
          <button className="retry-btn" onClick={onRetry}>
            🔄 Try Again
          </button>
        )}
      </div>
      
      <div className="troubleshooting">
        <h4>💡 Troubleshooting Tips</h4>
        <ul>
          <li>Make sure your Databricks workspace is accessible</li>
          <li>Verify your OpenAI API key is valid</li>
          <li>Check that you have at least one Genie space configured</li>
          <li>Try asking a different question about your data</li>
        </ul>
      </div>
    </div>
  );
};

export default ErrorDisplay;
