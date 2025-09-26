import React, { useState, useEffect } from 'react';
import { QueryFormProps, ExampleQuestion } from '../types';
import './QueryForm.css';

// Import example questions from external configuration
const loadExampleQuestions = async (): Promise<ExampleQuestion[]> => {
  try {
    // Fetch example questions from the backend
    const response = await fetch('/api/example-questions');
    if (response.ok) {
      const data = await response.json();
      return data.questions || [];
    }
  } catch (error) {
    console.warn('Failed to load example questions from server, using fallback');
  }
  
  // Fallback questions if server call fails
  return [
    {
      text: 'What are the top 5 products by total sales?',
      description: 'Top Products by Sales'
    },
    {
      text: 'Show me revenue by month for the last year',
      description: 'Revenue by Month'
    },
    {
      text: 'Which regions have the highest customer counts?',
      description: 'Customers by Region'
    },
    {
      text: 'What is the average order value by product category?',
      description: 'Average Order Value'
    }
  ];
};

const QueryForm: React.FC<QueryFormProps> = ({ onQuery, loading }) => {
  const [question, setQuestion] = useState('');
  const [exampleQuestions, setExampleQuestions] = useState<ExampleQuestion[]>([]);

  // Load example questions on component mount
  useEffect(() => {
    loadExampleQuestions().then(setExampleQuestions);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim()) {
      onQuery(question.trim());
    }
  };

  const handleExampleClick = (exampleText: string) => {
    setQuestion(exampleText);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="query-form-container">
      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-container">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your data..."
            className="query-textarea"
            maxLength={500}
            rows={4}
            disabled={loading}
          />
          <button
            type="submit"
            className={`submit-icon-btn ${loading ? 'loading' : ''}`}
            disabled={loading || !question.trim()}
            title={loading ? 'Processing...' : 'Send query (Enter)'}
          >
            {loading ? (
              <div className="spinner-small"></div>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            )}
          </button>
        </div>
        <div className="input-hint">
          <span>💡 Press Enter to send • Shift+Enter for new line</span>
        </div>
      </form>

      <div className="examples-section">
        <h3>💡 Example Questions</h3>
        <div className="examples-grid">
          {exampleQuestions.map((example, index) => (
            <button
              key={index}
              className="example-btn"
              onClick={() => handleExampleClick(example.text)}
              disabled={loading}
            >
              <span className="example-title">{example.description}</span>
              <span className="example-text">{example.text}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QueryForm;
