import React, { useState } from 'react';
import axios from 'axios';
import QueryForm from './components/QueryForm';
import ChartDisplay from './components/ChartDisplay';
import TextDisplay from './components/TextDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorDisplay from './components/ErrorDisplay';
import { GenieQueryResult, GenieChartResult, GenieTextResult, ApiError } from './types';
import './App.css';

const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<GenieQueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<string>('');

  const handleQuery = async (question: string) => {
    setLoading(true);
    setError(null);
    setData(null);
    setCurrentQuestion(question);

    try {
      const response = await axios.post<GenieQueryResult | ApiError>('/api/query', {
        question: question
      });

      if (response.data.success) {
        setData(response.data as GenieQueryResult);
      } else {
        setError((response.data as ApiError).error);
      }
    } catch (err: any) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.message) {
        setError(`Network error: ${err.message}`);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    if (currentQuestion) {
      handleQuery(currentQuestion);
    }
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>Genie Chat</h1>
          <p>Ask questions about your data</p>
        </div>
        
        <div className="sidebar-content">
          <QueryForm onQuery={handleQuery} loading={loading} />

          <div className="workflow-info">
            <h4>⚡ How it works</h4>
            <div className="workflow-steps">
              <div className="workflow-step">
                <span className="step-number">1</span>
                <div className="step-content">
                  <strong>Databricks Genie</strong>
                  <p>Converts your question to SQL</p>
                </div>
              </div>
              <div className="workflow-step">
                <span className="step-number">2</span>
                <div className="step-content">
                  <strong>AI Analysis</strong>
                  <p>GPT-5 recommends best visualization</p>
                </div>
              </div>
              <div className="workflow-step">
                <span className="step-number">3</span>
                <div className="step-content">
                  <strong>Interactive Charts</strong>
                  <p>Beautiful react-chartjs-2 visualizations</p>
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

      {/* Main Content Area */}
      <main className="main-content">
        <header className="main-header">
          <h1>Genie to Chart POC</h1>
          <p>AI-powered data visualization dashboard</p>
        </header>

        <div className="content-area">
          {loading && (
            <div className="loading-container">
              <LoadingSpinner />
            </div>
          )}
          
          {error && (
            <div className="error-container">
              <ErrorDisplay 
                error={error} 
                onRetry={currentQuestion ? handleRetry : undefined} 
              />
            </div>
          )}
          
          {data && !loading && !error && (
            <div className="results-container">
              {data.response_type === 'chart' ? (
                <>
                  {/* Question and Chart Results */}
                  <div className="chart-results-section">
                    <div className="results-header">
                      <h2>📈 Results for: "{data.question}"</h2>
                      {(data as GenieChartResult).is_mock_data && (
                        <div className="mock-data-badge">
                          🧪 Demo Data: Using mock data for demonstration
                        </div>
                      )}
                    </div>

                    {/* AI Data Summary */}
                    <div className="summary-highlight">
                      <div className="summary-content">
                        <h3>🧠 Key Insights</h3>
                        <p className="summary-text">{(data as GenieChartResult).data_summary.ai_summary}</p>
                      </div>
                    </div>

                    {/* Chart with expandable details */}
                    <div className="chart-section">
                      <ChartDisplay 
                        data={data as GenieChartResult} 
                        showDetailsToggle={true}
                        sqlQuery={(data as GenieChartResult).sql_query}
                        dataDetails={(data as GenieChartResult).data_summary}
                        chartReasoning={(data as GenieChartResult).chart_spec.reasoning}
                        chartType={(data as GenieChartResult).chart_spec.chart_type}
                        chartLibrary={(data as GenieChartResult).chart_spec.library}
                      />
                    </div>
                  </div>
                </>
              ) : (
                <TextDisplay data={data as GenieTextResult} />
              )}
            </div>
          )}

          {!loading && !error && !data && (
            <div className="welcome-container">
              <div className="welcome-content">
                <h2>Welcome to Genie to Chart POC</h2>
                <p className="welcome-description">
                  Transform natural language questions into beautiful, interactive charts using 
                  Databricks Genie and Azure OpenAI.
                </p>
                  <div className="welcome-cta">
                    <p>👈 <strong>Start by asking a question in the sidebar</strong></p>
                    <p className="welcome-hint">Click on any example question to get started, or type your own!</p>
                  </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;