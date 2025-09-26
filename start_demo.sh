#!/bin/bash

echo "🚀 Genie to Chart POC Setup & Demo"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env_template .env
    echo "⚠️  Please edit .env file with your credentials:"
    echo "   - DATABRICKS_HOST"
    echo "   - DATABRICKS_TOKEN" 
    echo "   - Azure OpenAI settings (ENDPOINT, API_KEY, DEPLOYMENT)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

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
echo "🎯 Choose demo mode:"
echo "1. Web Application (recommended)"
echo "2. Command Line Demo"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "🌐 Starting web application..."
        echo "Open http://localhost:5000 in your browser"
        python web_app.py
        ;;
    2)
        echo "💻 Starting command line demo..."
        python main_demo.py
        ;;
    *)
        echo "❌ Invalid choice. Please run again and enter 1 or 2."
        exit 1
        ;;
esac
