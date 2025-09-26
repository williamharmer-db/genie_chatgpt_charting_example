import React from 'react';
import './LoadingSpinner.css';

interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  message = "Processing your question..." 
}) => {
  return (
    <div className="loading-container">
      <div className="loading-spinner">
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
      </div>
      <h3 className="loading-title">{message}</h3>
      <p className="loading-subtitle">
        This may take a moment while we query your data and generate the visualization.
      </p>
      <div className="loading-steps">
        <div className="step">
          <span className="step-icon">📊</span>
          <span className="step-text">Querying Databricks Genie...</span>
        </div>
        <div className="step">
          <span className="step-icon">🤖</span>
          <span className="step-text">Getting AI visualization recommendations...</span>
        </div>
        <div className="step">
          <span className="step-icon">📈</span>
          <span className="step-text">Generating interactive chart...</span>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
