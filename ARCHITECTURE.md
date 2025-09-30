# Genie to Chart POC - Architecture Overview

## 🏗️ Project Structure

```
genie-to-chart-poc/
├── app.py                          # Main application entry point
├── start.sh                        # Quick start script
├── requirements.txt                # Python dependencies
├── README.md                       # Comprehensive documentation
├── ARCHITECTURE.md                 # This file - architecture overview
├── env_template                    # Environment variables template
├── .env                           # Environment configuration (not in git)
│
├── backend/                        # Backend Python application
│   ├── __init__.py
│   ├── api/                       # REST API layer
│   │   ├── __init__.py
│   │   └── routes.py              # All API endpoints and route handlers
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── conversation_manager.py # Conversation and message management
│   │   └── message_queue.py       # Thread-safe message queue system
│   ├── models/                    # Data models and schemas
│   │   ├── __init__.py
│   │   └── conversation.py        # Conversation, Message, and Queue models
│   ├── services/                  # External service integrations
│   │   ├── __init__.py
│   │   ├── chatgpt_client.py      # Azure OpenAI integration
│   │   ├── genie_client.py        # Databricks Genie integration
│   │   └── visualization_engine.py # Chart generation engine
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       └── example_questions.py   # Sample questions for UI
│
└── frontend/                       # React TypeScript frontend
    ├── build/                     # Production build output
    ├── public/                    # Static assets
    ├── src/
    │   ├── App.tsx                # Main React application
    │   ├── App.css                # Global styles
    │   ├── components/            # React components
    │   │   ├── ChatInterface.tsx  # Main chat interface
    │   │   ├── ChatMessage.tsx    # Individual message display
    │   │   ├── ConversationList.tsx # Sidebar conversation list
    │   │   └── *.css              # Component styles
    │   └── types/
    │       └── index.ts           # TypeScript type definitions
    ├── package.json               # Node.js dependencies
    └── tsconfig.json              # TypeScript configuration
```

## 🔄 Application Flow

### 1. Message Processing Pipeline
```
User Input → Queue → Worker Thread → Genie → AI Analysis → Chart Generation → Response
```

### 2. Key Components

#### **Message Queue System** (`backend/core/message_queue.py`)
- Thread-safe queue with configurable workers (default: 2)
- Status tracking: `queued` → `processing` → `completed`/`failed`
- Automatic cleanup and error isolation
- Prevents concurrent processing conflicts

#### **Conversation Manager** (`backend/core/conversation_manager.py`)
- Session-based conversation persistence
- Message history and context management
- Automatic conversation title generation
- Context building for Genie queries

#### **Service Layer** (`backend/services/`)
- **Genie Client**: Databricks integration with exponential backoff
- **ChatGPT Client**: Azure OpenAI integration for insights
- **Visualization Engine**: Chart.js configuration generation

#### **API Layer** (`backend/api/routes.py`)
- RESTful endpoints for all functionality
- Queue-based message processing
- Status polling endpoints
- Error handling and recovery

## 🚀 Key Improvements Made

### 1. **Organized Structure**
- Clear separation of concerns
- Proper Python package structure
- Logical grouping of functionality
- Easy to navigate and understand

### 2. **Concurrent Processing**
- Thread-safe message queue
- Multiple conversations can process simultaneously
- No more connection conflicts
- Graceful error handling

### 3. **Per-Conversation State Management**
- Loading states isolated to specific conversations
- No cross-conversation UI interference
- Better user experience

### 4. **Improved Error Handling**
- Comprehensive error tracking
- Graceful degradation to mock data
- User-friendly error messages
- Automatic retry mechanisms

### 5. **Better Documentation**
- Comprehensive README
- Inline code documentation
- Architecture overview
- Clear setup instructions

## 🔧 Configuration

### Environment Variables
All configuration is managed through environment variables with sensible defaults:

- **Databricks**: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `GENIE_SPACE_ID`
- **Azure OpenAI**: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`
- **Queue Settings**: `MAX_QUEUE_WORKERS`, `MAX_QUEUE_SIZE`
- **Rate Limiting**: `MAX_RETRIES`, `INITIAL_BACKOFF`, `MAX_BACKOFF`

### Application Settings
Configuration is centralized in `backend/core/config.py` using Pydantic for validation and type safety.

## 🧪 Testing and Development

### Quick Start
```bash
./start.sh
```

### Manual Start
```bash
# Install dependencies
pip install -r requirements.txt

# Build frontend
cd frontend && npm ci && npm run build && cd ..

# Start application
python app.py
```

### Development Mode
```bash
# Backend only
python app.py

# Frontend development server (optional)
cd frontend && npm start
```

## 📊 API Endpoints

### Core Endpoints
- `GET /api/health` - Health check and system status
- `GET /api/conversations` - List all conversations
- `POST /api/conversations` - Create new conversation
- `POST /api/conversations/{id}/messages` - Send message (returns queue ID)
- `GET /api/messages/{id}/status` - Check message processing status

### Utility Endpoints
- `GET /api/examples` - Get example questions
- `GET /api/queue/status` - Queue system information

## 🔮 Future Enhancements

1. **WebSocket Integration**: Real-time updates instead of polling
2. **Authentication**: Multi-user support with proper auth
3. **Persistence**: Database integration for conversation storage
4. **Advanced Charts**: More visualization types and customization
5. **Export Features**: PDF/PNG export for charts and conversations
6. **Dashboard Mode**: Multiple conversations in a dashboard view

## 🛠️ Development Guidelines

### Adding New Features
1. **Models**: Define data structures in `backend/models/`
2. **Services**: Add external integrations in `backend/services/`
3. **API**: Create endpoints in `backend/api/routes.py`
4. **Frontend**: Add components in `frontend/src/components/`

### Code Style
- Use type hints in Python
- Follow PEP 8 style guidelines
- Use TypeScript for all frontend code
- Document public functions and classes
- Write tests for new functionality

### Error Handling
- Use structured logging with Loguru
- Provide user-friendly error messages
- Implement graceful degradation
- Add proper exception handling
