import React from 'react';
import { GenieTextResult } from '../types';
import './TextDisplay.css';

interface TextDisplayProps {
  data: GenieTextResult;
}

const TextDisplay: React.FC<TextDisplayProps> = ({ data }) => {
  return (
    <div className="text-display">
      <div className="text-content">
        <div className="text-header">
          <h2>💬 Genie Response</h2>
          <p className="text-subtitle">Question: "{data.question}"</p>
        </div>

        <div className="text-response">
          <div className="response-content">
            {data.text_response.split('\n').map((line, index) => (
              <p key={index} className={line.trim() === '' ? 'empty-line' : ''}>
                {line.trim() === '' ? '\u00A0' : line}
              </p>
            ))}
          </div>
        </div>

        {data.sql_query && (
          <div className="sql-section">
            <h4>📝 Generated SQL Query</h4>
            <pre className="sql-code">{data.sql_query}</pre>
          </div>
        )}

        <div className="info-section">
          <div className="info-card">
            <h4>ℹ️ Response Information</h4>
            <p><strong>Type:</strong> Text Response</p>
            <p><strong>Source:</strong> Databricks Genie</p>
            <p><strong>Processing:</strong> No chart generated (text-only response)</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TextDisplay;
