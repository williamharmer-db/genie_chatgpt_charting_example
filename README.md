# Genie to Chart POC

A proof of concept that demonstrates the complete flow from data query to interactive visualization:

1. **📊 Query Databricks Genie API** - Ask natural language questions about your data
2. **🔵 Azure OpenAI Visualization Recommendations** - GPT analyzes the data and suggests the best chart type
3. **📈 Interactive React Charts** - Generate react-chartjs-2 components for beautiful, interactive visualizations

## 🎯 What This POC Demonstrates

- **Seamless Data-to-Viz Pipeline**: From natural language query to interactive chart in seconds
- **AI-Driven Visualization**: ChatGPT intelligently chooses the best chart type based on data characteristics
- **Modern React Frontend**: TypeScript + react-chartjs-2 for professional, responsive UI
- **Production-Ready Components**: Modular, well-structured code that can be extended
- **Multiple Interfaces**: CLI demo, vanilla web app, and modern React application

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your credentials:

```bash
cp env_template .env
```

Edit `.env` with your actual credentials:

```bash
# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-personal-access-token
GENIE_SPACE_ID=your-genie-space-id  # Optional - will auto-detect

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-01
```


### 3. Choose Your Demo Mode

#### Option A: React Application (Recommended) 🌟
```bash
./start_react_demo.sh
```
This builds and serves the React frontend with react-chartjs-2 charts.

#### Option B: Development Mode 
```bash
./dev_mode.sh
```
Runs both Flask API (port 5000) and React dev server (port 3000) for development.

#### Option C: Build from Scratch
```bash
./build.sh        # Build the React frontend
python web_app.py  # Start the Flask server
```

#### Option D: Command Line Demo
```bash
python main_demo.py
```

#### Option E: Legacy Web Interface
```bash
python web_app.py
```
(Serves React build if available, otherwise shows build instructions)

## 🌟 Features

### 📊 Data Querying
- Uses the proven Databricks Genie client from the existing `genie_conversation_api` project
- Handles rate limiting with exponential backoff
- Fetches actual query results, not just SQL

### 🤖 AI Visualization Recommendations  
- ChatGPT analyzes your data structure and original question
- Recommends optimal chart types (bar, line, pie, scatter, etc.)
- Provides reasoning for visualization choices
- Handles multiple data formats and edge cases

### 📈 Interactive React Charts
- **react-chartjs-2** components for modern, responsive charts
- **TypeScript** for type safety and better development experience
- **Component-based architecture** for reusability and maintainability
- Beautiful, responsive charts that work on all devices
- Supports all major chart types with smooth animations
- Real-time data updates and interactive tooltips

### 🌐 Modern Web Interface
- **React + TypeScript** frontend with modern design
- **Flask API** backend serving both API and React build
- **CORS-enabled** for development flexibility
- Real-time query processing with loading states
- Example questions to get started
- Complete data pipeline visualization
- Responsive design for mobile and desktop

## 📁 Project Structure

```
genie-to-chart-poc/
├── config.py              # Configuration management
├── genie_client.py         # Simplified Databricks Genie client  
├── chatgpt_client.py       # OpenAI client for visualization recommendations
├── visualization_engine.py # Chart.js configuration generator
├── main_demo.py           # Command line demo script
├── web_app.py             # Flask web application with React serving
├── frontend/              # React TypeScript application
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── ChartDisplay.tsx     # react-chartjs-2 chart component
│   │   │   ├── QueryForm.tsx        # Query input form
│   │   │   ├── LoadingSpinner.tsx   # Loading animation
│   │   │   └── ErrorDisplay.tsx     # Error handling
│   │   ├── types/         # TypeScript type definitions
│   │   └── App.tsx        # Main React application
│   ├── package.json       # Node.js dependencies
│   └── build/             # Production build (created by npm run build)
├── templates/
│   └── index.html         # Legacy web interface
├── build.sh               # Build script for React frontend
├── start_react_demo.sh    # Start production React app
├── dev_mode.sh           # Development mode (Flask + React dev server)
├── start_demo.sh         # Original demo launcher
├── requirements.txt       # Python dependencies
├── env_template          # Environment configuration template
└── README.md             # This file
```

## 🔧 Architecture

### Data Flow
1. **User Question** → Natural language query (e.g., "What are the top 5 products by sales?")
2. **Genie API** → Converts to SQL and executes against your data
3. **Data Processing** → Extracts structured results (columns, rows, data types)
4. **ChatGPT Analysis** → Analyzes data and recommends visualization approach
5. **Chart Generation** → Creates Chart.js configuration
6. **Visualization** → Renders interactive chart in browser

### Key Components

#### GenieClient
- Simplified version of the existing Genie conversation API
- Handles authentication, rate limiting, and result fetching
- Returns structured `GenieQueryResult` objects

#### ChatGPTClient  
- Sends data structure and context to GPT-4
- Receives structured chart specifications
- Includes fallback logic for robust operation

#### VisualizationEngine
- Converts AI recommendations to Chart.js configurations
- Generates complete HTML pages with charts
- Handles multiple chart types and styling

## 🎯 Example Usage

### Web Interface
1. Open http://localhost:5000
2. Enter a question like "Show me revenue by product category"
3. Watch as the system:
   - Queries your Databricks data
   - Gets AI visualization recommendations
   - Generates an interactive chart
   - Displays SQL, data preview, and reasoning

### Command Line
```python
from main_demo import GenieToChartPOC

poc = GenieToChartPOC()
html_file = poc.run_demo("What are the top 10 customers by total orders?")
# Opens chart in browser automatically
```

## 🛡️ Error Handling

The POC includes robust error handling for:
- **API Rate Limits**: Exponential backoff for both Databricks and OpenAI
- **Network Issues**: Retry logic and graceful degradation
- **Data Edge Cases**: Fallback chart types when AI analysis fails
- **Configuration Errors**: Clear error messages for missing credentials

## 🔍 Key Implementation Details

### Genie Integration
```python
# Query data using natural language
result = genie_client.query_data("What are the top 5 products by sales?")
# Returns: SQL query + structured data + column information
```

### AI Visualization  
```python
# Get AI recommendation for chart type
chart_spec = chatgpt_client.recommend_visualization(
    data=result.data,
    columns=result.columns, 
    question="What are the top 5 products by sales?",
    sql_query=result.sql_query
)
# Returns: Chart type, configuration, and reasoning
```

### Chart Generation
```python
# Generate interactive Chart.js configuration
chart_config = viz_engine.generate_chartjs_config(chart_spec)
# Returns: Complete Chart.js config ready for rendering
```

## 🎨 Customization

### Adding New Chart Types
1. Update `ChatGPTClient` prompt to include new chart types
2. Add chart type handling in `VisualizationEngine._prepare_chartjs_data()`
3. Update web interface chart type display

### Extending Data Sources
1. Create new client classes following the `GenieClient` pattern
2. Implement `query_data()` method returning `GenieQueryResult`
3. Update main demo to support multiple data sources

### Custom AI Models
1. Replace OpenAI client in `ChatGPTClient`
2. Adjust prompts for different model capabilities
3. Update fallback logic as needed

## 🤝 Integration with Existing Project

This POC builds on the `genie_conversation_api` project:

- **Reuses**: Authentication, rate limiting, Genie SDK integration
- **Simplifies**: Removes conversation management for single-query use case  
- **Extends**: Adds AI visualization and Chart.js generation

The simplified `GenieClient` can easily be replaced with the full conversation API for more complex use cases.

## 🎉 Demo Results

The POC successfully demonstrates:

✅ **Natural Language to SQL**: "Show me top products" → `SELECT ProductName, SUM(Sales) FROM...`  
✅ **AI Chart Selection**: Automatically chooses bar chart for ranked categorical data  
✅ **Interactive Visualization**: Beautiful Chart.js charts with hover effects and legends  
✅ **Complete Pipeline**: End-to-end flow in under 30 seconds  
✅ **Error Resilience**: Graceful handling of API limits and edge cases

## 🔮 Next Steps

For production deployment:

1. **Caching**: Add Redis/database caching for repeated queries
2. **Authentication**: Add user authentication and workspace isolation  
3. **Scaling**: Deploy with gunicorn/uwsgi for production traffic
4. **Monitoring**: Add logging, metrics, and health checks
5. **Chart Library Options**: Support for D3.js, Plotly, or other libraries

## 🆘 Troubleshooting

### Common Issues

**Missing Environment Variables**
```bash
❌ Missing required environment variables: DATABRICKS_TOKEN
```
→ Check your `.env` file has all required variables

**Genie Space Not Found**  
```bash
❌ No Genie spaces found
```
→ Ensure you have access to at least one Genie space in your Databricks workspace

**OpenAI API Errors**
```bash
❌ OpenAI API rate limit exceeded
```
→ The system will automatically retry with backoff

**No Data Returned**
```bash
❌ No data returned from Genie query  
```
→ Try rephrasing your question or check data availability

### Health Check
Visit `/api/health` to verify system configuration and connectivity.

## 📞 Support

This POC demonstrates the core concept and provides a foundation for production implementation. The modular architecture makes it easy to extend and customize for specific use cases.
