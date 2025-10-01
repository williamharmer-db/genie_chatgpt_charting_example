"""
Genie to Chart POC - Main Application

A Flask-based web application that provides conversational data analysis
using Databricks Genie and Azure OpenAI with an intelligent message queue system.

Key Features:
- Conversational interface for data queries
- Concurrent message processing with queue system
- Real-time chart generation and AI insights
- Session-based conversation management
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from flask import Flask
from backend.api.routes import register_routes
from backend.core.message_queue import message_queue
from backend.core.config import settings
from loguru import logger


def create_app() -> Flask:
    """
    Application factory function.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, static_folder='frontend/build', static_url_path='')
    app.secret_key = os.urandom(24)  # For session management
    
    # Initialize queue system for WSGI deployment
    initialize_queue_system()
    
    # Register all API routes
    register_routes(app)
    
    return app


def check_environment() -> bool:
    """
    Verify that all required environment variables are set.
    
    Returns:
        bool: True if all required variables are present, False otherwise
    """
    # Only Azure OpenAI variables are required
    # Databricks variables are optional (can use default authentication)
    required_vars = [
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_API_KEY", 
        "AZURE_OPENAI_DEPLOYMENT"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error("❌ Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("Please set these environment variables or create a .env file")
        return False
    
    return True


def initialize_queue_system():
    """Initialize and start the message queue system."""
    from backend.api.routes import process_message, queue_status_callback
    
    # Configure the message queue
    message_queue.set_message_processor(process_message)
    message_queue.set_status_callback(queue_status_callback)
    
    # Start the queue workers
    message_queue.start()
    logger.info("📬 Message queue system started")


def shutdown_queue_system():
    """Gracefully shutdown the message queue system."""
    logger.info("📬 Stopping message queue...")
    message_queue.stop()


def main():
    """Main application entry point."""
    # Check environment setup
    if not check_environment():
        sys.exit(1)
    
    # Determine if running in Databricks environment
    is_databricks = os.getenv('FLASK_ENV') == 'production' or os.getenv('DATABRICKS_RUNTIME_VERSION')
    port = 8080 if is_databricks else 5000
    debug = not is_databricks
    
    logger.info("🚀 Starting Genie to Chart POC Web App")
    logger.info(f"📊 Databricks: {os.getenv('GENIE_DATABRICKS_HOST') or 'Using default authentication'}")
    logger.info(f"🤖 OpenAI: Configured")
    
    # Initialize the message queue system
    initialize_queue_system()
    
    # Create and configure the Flask app
    app = create_app()
    
    if is_databricks:
        logger.info(f"🌐 Running in Databricks Apps environment on port {port}")
    else:
        logger.info(f"🌐 Open http://localhost:{port} in your browser")
    
    try:
        # Run the Flask server
        app.run(debug=debug, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        shutdown_queue_system()


# Create Flask app instance for Gunicorn (WSGI server)
app = create_app()

if __name__ == '__main__':
    main()
