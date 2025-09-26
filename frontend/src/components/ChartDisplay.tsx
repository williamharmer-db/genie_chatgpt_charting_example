import React, { useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import {
  Bar,
  Line,
  Pie,
  Doughnut,
  Scatter,
  PolarArea,
} from 'react-chartjs-2';
import { ChartComponentProps } from '../types';
import './ChartDisplay.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const ChartDisplay: React.FC<ChartComponentProps> = ({ 
  data, 
  showDetailsToggle = false, 
  sqlQuery = '', 
  dataDetails, 
  chartReasoning = '', 
  chartType = '', 
  chartLibrary = '' 
}) => {
  const { chart_config, chart_spec } = data;
  const [showDetails, setShowDetails] = useState(false);

  const renderChart = () => {
    const chartProps = {
      data: chart_config.data,
      options: chart_config.options,
    };

    switch (chart_spec.chart_type.toLowerCase()) {
      case 'bar':
        return <Bar {...chartProps} />;
      case 'line':
        return <Line {...chartProps} />;
      case 'pie':
        return <Pie {...chartProps} />;
      case 'doughnut':
        return <Doughnut {...chartProps} />;
      case 'scatter':
        return <Scatter {...chartProps} />;
      case 'polararea':
        return <PolarArea {...chartProps} />;
      default:
        return <Bar {...chartProps} />;
    }
  };

  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  return (
    <div className="chart-display">
      <div className="chart-header">
        {showDetailsToggle && (
          <button 
            className="details-toggle-btn" 
            onClick={toggleDetails}
            title={showDetails ? "Hide technical details" : "Show technical details"}
          >
            🧠
          </button>
        )}
      </div>

      <div className="chart-container">
        {renderChart()}
      </div>
      
      <div className="chart-info">
        <div className="chart-stats">
          <span><strong>Data Points:</strong> {chart_config.data.datasets[0]?.data?.length || 0}</span>
          <span><strong>Chart Type:</strong> {chart_spec.chart_type}</span>
        </div>
      </div>

      {/* Expandable Technical Details */}
      {showDetailsToggle && showDetails && (
        <div className="technical-details">
          <div className="details-header">
            <h3>🧠 Technical Details & Chain of Thought</h3>
          </div>
          
          {/* SQL Query */}
          <div className="detail-section">
            <h4>📝 Generated SQL Query</h4>
            <div className="sql-card">
              <pre className="sql-code">{sqlQuery}</pre>
            </div>
          </div>

          {/* Data Details */}
          {dataDetails && (
            <div className="detail-section">
              <h4>🗃️ Data Retrieved</h4>
              <div className="data-card">
                <div className="data-meta">
                  <span><strong>Columns:</strong> {dataDetails.columns.join(', ')}</span>
                  <span><strong>Rows:</strong> {dataDetails.row_count}</span>
                </div>
                <div className="data-table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {dataDetails.columns.map((column, index) => (
                          <th key={index}>{column}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {dataDetails.sample_data.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {row.map((cell, cellIndex) => (
                            <td key={cellIndex}>{cell}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Chart Reasoning */}
          <div className="detail-section">
            <h4>🤖 Chart Type Selection</h4>
            <div className="reasoning-card">
              <div className="chart-meta">
                <span><strong>Chart Type:</strong> {chartType}</span>
                <span><strong>Library:</strong> {chartLibrary}</span>
              </div>
              <p className="reasoning-text">{chartReasoning}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChartDisplay;
