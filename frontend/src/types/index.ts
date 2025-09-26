// Type definitions for the Genie to Chart POC

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

export interface ChartComponentProps {
  data: GenieChartResult;
  showDetailsToggle?: boolean;
  sqlQuery?: string;
  dataDetails?: {
    columns: string[];
    row_count: number;
    sample_data: any[][];
    ai_summary: string;
  };
  chartReasoning?: string;
  chartType?: string;
  chartLibrary?: string;
}

export interface QueryFormProps {
  onQuery: (question: string) => void;
  loading: boolean;
}

export interface ExampleQuestion {
  text: string;
  description: string;
}
