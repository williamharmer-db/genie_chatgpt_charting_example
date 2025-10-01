# Genie to Chart POC

A conversational data analysis application that combines Databricks Genie with Azure OpenAI to provide intelligent chart generation and insights through natural language queries.

## 🚀 Overview

This application provides a chat-based interface for data analysis where users can ask questions in natural language and receive both intelligent visualizations and AI-powered insights. The system uses Databricks Genie for data querying and Azure OpenAI for generating summaries and visualization recommendations.

### Key Features

- **Conversational Interface**: Ask questions about your data in plain English
- **Intelligent Visualizations**: Automatic chart generation with AI-powered recommendations
- **Concurrent Processing**: Queue-based message processing for handling multiple conversations
- **Real-time Updates**: Live status tracking and polling for message completion
- **Session Management**: Persistent conversations with message history
- **Error Handling**: Graceful error handling with fallback to mock data for demos

## 🏗️ Architecture

### Backend Structure
```
backend/
├── api/           # REST API endpoints and route handlers
├── core/          # Core business logic and configuration
├── models/        # Data models and schemas
├── services/      # External service integrations
└── utils/         # Utility functions and helpers
```

### Technology Stack

**Backend:**
- Flask (Web framework)
- Databricks SDK (Data querying)
- Azure OpenAI (AI insights and recommendations)
- Threading (Concurrent message processing)
- Loguru (Logging)

**Frontend:**
- React with TypeScript
- Chart.js (Data visualization)
- Axios (HTTP client)
- CSS3 (Styling)

### Frontend Architecture

#### Component Hierarchy
```
App.tsx (Root Container)
├── ConversationList.tsx (Sidebar)
│   └── Individual conversation items
└── ChatInterface.tsx (Main Chat Area)
    ├── Message History
    └── ChatMessage.tsx (Individual Messages)
        ├── User Messages
        ├── Assistant Text Responses
        └── Chart Displays (with Chart.js integration)
```

#### State Management
The application uses React's built-in state management with strategic state lifting:

- **Global App State**: Manages conversations list, active conversation, and per-conversation loading states
- **Conversation-Specific State**: Each conversation tracks its own messages and metadata
- **Message Queue Integration**: Real-time polling for message status updates

#### Key Frontend Features

**Per-Conversation Loading States:**
```typescript
const [conversationLoadingStates, setConversationLoadingStates] = 
  useState<Record<string, boolean>>({});
```
- Prevents global loading states that affect all conversations
- Each conversation shows loading independently
- Loading state tied to specific conversation ID

**Message Status Polling:**
```typescript
const pollForMessageCompletion = async (messageId: string, conversationId: string) => {
  // Polls every 1 second for up to 60 seconds
  // Updates conversation when message completes
  // Handles timeout and error scenarios
};
```

**Chart Integration:**
- Dynamic Chart.js configuration based on data type
- Responsive chart sizing and styling
- Support for multiple chart types (line, bar, pie, etc.)
- Error fallbacks for chart rendering issues

**API Communication:**
- Axios-based HTTP client with error handling
- RESTful API integration with Flask backend
- Automatic retry logic for failed requests
- Real-time status checking via polling

#### Component Responsibilities

**App.tsx:**
- Application-wide state management
- API communication and error handling
- Conversation and message lifecycle management
- Per-conversation loading state coordination

**ConversationList.tsx:**
- Sidebar conversation management
- Conversation creation and selection
- Conversation metadata display
- Active conversation highlighting

**ChatInterface.tsx:**
- Message input and submission
- Message history display
- Loading state presentation
- Error message display

**ChatMessage.tsx:**
- Individual message rendering
- Chart display integration
- Message type differentiation (user/assistant/chart)
- Responsive message layout

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Databricks workspace with Genie enabled
- Azure OpenAI account

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd genie-to-chart-poc
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the root directory:
```bash
# Databricks Configuration
GENIE_DATABRICKS_HOST=https://your-workspace.cloud.databricks.com/
GENIE_DATABRICKS_TOKEN=your-databricks-token
GENIE_SPACE_ID=your-genie-space-id  # Optional

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-06-01

# Optional: Queue Configuration
MAX_QUEUE_WORKERS=2
MAX_QUEUE_SIZE=50

# Optional: Rate Limiting
MAX_RETRIES=3
INITIAL_BACKOFF=1.0
MAX_BACKOFF=60.0
BACKOFF_MULTIPLIER=2.0
```

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Build Frontend
```bash
npm run build
```

## 🚀 Running the Application

### Local Development Mode

#### Start Backend Server
```bash
python app.py
```

#### Start Frontend Development Server (Optional)
```bash
cd frontend
npm start
```

The application will be available at `http://localhost:5000`

### Databricks App Deployment

This application can be deployed as a native Databricks App for production use:

```bash
# Deploy to Databricks
databricks apps deploy genie-chart-app --source-path .
```

**Benefits of Databricks deployment:**
- 🔐 **Native Authentication**: Direct access to Databricks APIs
- 🚀 **Auto-scaling**: Scales with Databricks infrastructure  
- 🛡️ **Enterprise Security**: Secure secret management and network isolation
- 📊 **Built-in Monitoring**: Integrated logging and monitoring
- 💰 **Cost Efficient**: Pay only for compute resources used

See [DATABRICKS_DEPLOYMENT.md](DATABRICKS_DEPLOYMENT.md) for detailed deployment instructions.

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GENIE_DATABRICKS_HOST` | Yes | - | Your Databricks workspace URL |
| `GENIE_DATABRICKS_TOKEN` | Yes | - | Databricks personal access token |
| `GENIE_SPACE_ID` | No | - | Specific Genie space ID (uses first available if not set) |
| `AZURE_OPENAI_ENDPOINT` | Yes | - | Azure OpenAI service endpoint |
| `AZURE_OPENAI_API_KEY` | Yes | - | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | - | Azure OpenAI deployment name |
| `AZURE_OPENAI_API_VERSION` | No | 2024-06-01 | Azure OpenAI API version |
| `MAX_QUEUE_WORKERS` | No | 2 | Number of concurrent message processing workers |
| `MAX_QUEUE_SIZE` | No | 50 | Maximum queue size for pending messages |

### Queue System

The application uses a thread-safe message queue system to handle concurrent conversations:

- **Concurrent Workers**: Process multiple messages simultaneously
- **Status Tracking**: Real-time status updates (queued → processing → completed/failed)
- **Error Isolation**: Failures in one conversation don't affect others
- **Rate Limiting Protection**: Built-in exponential backoff for API calls

## 📡 API Endpoints

### Health & Status
- `GET /api/health` - Health check and queue status
- `GET /api/queue/status` - Detailed queue information

### Conversations
- `GET /api/conversations` - List all conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{id}` - Get specific conversation
- `DELETE /api/conversations/{id}` - Delete conversation

### Messages
- `POST /api/conversations/{id}/messages` - Send message (returns queue ID)
- `GET /api/messages/{id}/status` - Check message processing status

### Utilities
- `GET /api/examples` - Get example questions

## 🧪 Testing

### Verify Environment Setup
The application will automatically validate your environment variables on startup. If any required variables are missing, you'll see a clear error message with instructions.

## 🔄 How It Works

1. **User Input**: User types a natural language question about their data
2. **Queue Processing**: Message is added to the processing queue and assigned a unique ID
3. **Context Building**: System builds conversational context from previous messages
4. **Genie Query**: Enhanced question is sent to Databricks Genie for data retrieval
5. **AI Analysis**: Azure OpenAI analyzes the data and provides insights
6. **Chart Generation**: System creates appropriate visualizations based on data type
7. **Response Delivery**: User receives charts, insights, and explanations
8. **Status Updates**: Frontend polls for completion and displays results

## 📊 Supported Chart Types

- Bar Charts (vertical/horizontal)
- Line Charts (single/multiple series)
- Pie Charts
- Doughnut Charts
- Scatter Plots
- Area Charts

## 🛡️ Error Handling

- **Graceful Degradation**: Falls back to mock data for demonstrations
- **Rate Limiting**: Automatic retry with exponential backoff
- **Connection Errors**: Detailed error messages and recovery suggestions
- **Queue Management**: Failed messages are properly tracked and reported

## 🎨 Frontend Features

### User Experience
- **Per-conversation Loading States**: Loading indicators only appear in active conversations
- **Real-time Polling**: Automatic status checking for queued messages  
- **Responsive Design**: Works on desktop and mobile devices
- **Error Display**: User-friendly error messages and recovery options
- **Intuitive Navigation**: Sidebar conversation switching with persistent state
- **Interactive Charts**: Hover effects, tooltips, and responsive resizing

## 🔧 Development

### Project Structure
```
genie-to-chart-poc/
├── app.py                 # Main application entry point
├── backend/               # Backend Python modules
│   ├── api/              # REST API routes
│   ├── core/             # Core business logic
│   ├── models/           # Data models
│   ├── services/         # External service clients
│   └── utils/            # Utility functions
├── frontend/             # React frontend application
└── requirements.txt      # Python dependencies
```

### Adding New Features

1. **Backend Changes**: Add new routes in `backend/api/routes.py`
2. **Frontend Changes**: Create components in `frontend/src/components/`
3. **Models**: Define data structures in `backend/models/`
4. **Services**: Add external integrations in `backend/services/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📝 License

This project is provided as-is without any license or warranty. Use at your own discretion.

## 🆘 Troubleshooting

### Common Issues

**Environment Variables Not Loading**
- Ensure `.env` file is in the root directory
- Check for typos in variable names
- Verify no extra spaces around values

**Databricks Connection Issues**
- Verify your workspace URL format
- Check that your personal access token has sufficient permissions
- Ensure Genie is enabled in your workspace

**Azure OpenAI Connection Issues**
- Verify your endpoint URL is correct
- Check that your deployment name matches the configured model
- Ensure your API key has not expired

**Queue Processing Issues**
- Check queue status at `/api/queue/status`
- Monitor application logs for error details
- Restart the application to reset the queue

### Getting Help

- Check the application logs for detailed error messages
- Use the health check endpoint (`/api/health`) to verify system status
- Review the troubleshooting section above
- Open an issue on the repository for persistent problems

## 🎯 Future Enhancements

- WebSocket support for real-time updates
- Multi-user support with authentication
- Advanced chart customization options
- Export functionality for charts and data
- Integration with additional data sources
- Dashboard creation and sharing capabilities