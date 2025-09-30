#!/bin/bash

echo "🚀 Genie to Chart POC - React Edition"
echo "====================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f env_template ]; then
        cp env_template .env
    echo "⚠️  Please edit .env file with your credentials:"
    echo "   - DATABRICKS_HOST"
    echo "   - DATABRICKS_TOKEN" 
    echo "   - Azure OpenAI settings (ENDPOINT, API_KEY, DEPLOYMENT)"
        echo ""
        echo "Then run this script again."
        exit 1
    else
        echo "❌ Error: env_template file not found"
        exit 1
    fi
fi

# Check if React build exists
if [ ! -d "frontend/build" ]; then
    echo "🏗️  React build not found. Building now..."
    ./build.sh
    if [ $? -ne 0 ]; then
        echo "❌ Build failed. Please check the errors above."
        exit 1
    fi
fi

# Check environment variables
echo "🔍 Checking environment configuration..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = ['DATABRICKS_HOST', 'DATABRICKS_TOKEN', 'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_DEPLOYMENT']
missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print('❌ Missing environment variables: ' + ', '.join(missing))
    print('Please edit .env file with your credentials')
    exit(1)
else:
    print('✅ Environment configured correctly')
"

if [ $? -ne 0 ]; then
    echo "Please configure your .env file and try again"
    exit 1
fi

echo ""
echo "🌐 Starting React-powered Genie to Chart POC..."
echo "📊 Databricks Genie + 🔵 Azure OpenAI + ⚛️ React + 📈 react-chartjs-2"
echo ""
echo "🔗 Open http://localhost:5000 in your browser"
echo "💡 The React frontend is served by the Flask backend"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python web_app.py
