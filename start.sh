#!/bin/bash

# Genie to Chart POC - Startup Script

echo "🚀 Starting Genie to Chart POC"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your configuration."
    echo "See env_template for required variables."
    exit 1
fi

# Check if virtual environment should be activated
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update Python dependencies
echo "📋 Installing Python dependencies..."
pip install -r requirements.txt

# Build frontend if needed
if [ ! -d "frontend/build" ] || [ "frontend/package.json" -nt "frontend/build" ]; then
    echo "🔨 Building frontend..."
    cd frontend
    npm ci
    npm run build
    cd ..
fi

echo "🌟 Starting application..."
echo "🌐 Visit http://localhost:5000 when ready"
echo ""

# Start the application
python app.py
