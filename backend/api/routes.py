"""
API Routes for Genie to Chart POC

This module defines all REST API endpoints for the application,
including conversation management and message processing.
"""

import os
import random
from typing import Dict, Any
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from loguru import logger

from ..core.conversation_manager import conversation_manager
from ..core.message_queue import message_queue, MessageStatus
from ..services.genie_client import GenieClient
from ..services.chatgpt_client import ChatGPTClient
from ..services.visualization_engine import VisualizationEngine
from ..utils.example_questions import get_example_questions


# Initialize service clients
genie_client = GenieClient()
chatgpt_client = ChatGPTClient()
viz_engine = VisualizationEngine()


def register_routes(app: Flask) -> None:
    """
    Register all API routes with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Enable CORS for session management
    CORS(app, supports_credentials=True)
    
    # Static file serving
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve React frontend static files."""
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    # API Routes
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'message': 'Genie to Chart POC API is running',
            'queue_info': message_queue.get_queue_info()
        })
    
    @app.route('/api/examples', methods=['GET'])
    def get_examples():
        """Get example questions for the interface."""
        try:
            examples = get_example_questions()
            return jsonify({'success': True, 'examples': examples})
        except Exception as e:
            logger.error(f"Error loading example questions: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Conversation Management
    @app.route('/api/conversations', methods=['GET'])
    def get_conversations():
        """Get all conversations for the current session."""
        try:
            conversations = conversation_manager.get_all_conversations()
            return jsonify({'success': True, 'conversations': conversations})
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/conversations', methods=['POST'])
    def create_conversation():
        """Create a new conversation."""
        try:
            session_id = session.get('session_id') or str(os.urandom(16).hex())
            session['session_id'] = session_id
            
            conversation_id = conversation_manager.create_conversation(session_id=session_id)
            
            return jsonify({
                'success': True,
                'conversation_id': conversation_id,
                'message': 'Conversation created successfully'
            })
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/conversations/<conversation_id>', methods=['GET'])
    def get_conversation(conversation_id):
        """Get a specific conversation with all messages."""
        try:
            conversation = conversation_manager.get_conversation(conversation_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found, creating new one")
                session_id = session.get('session_id') or str(os.urandom(16).hex())
                session['session_id'] = session_id
                new_conversation_id = conversation_manager.create_conversation(
                    title="New Conversation", 
                    session_id=session_id
                )
                conversation = conversation_manager.get_conversation(new_conversation_id)
                
            return jsonify({
                'success': True,
                'conversation': conversation.to_dict() if conversation else None,
                'new_conversation_id': conversation.id if conversation else None
            })
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
    def delete_conversation(conversation_id):
        """Delete a conversation."""
        try:
            conversation_manager.delete_conversation(conversation_id)
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Message Processing
    @app.route('/api/conversations/<conversation_id>/messages', methods=['POST'])
    def add_message_to_conversation(conversation_id):
        """Add a message to a conversation queue for processing."""
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({'success': False, 'error': 'Message is required'}), 400
            
            user_message = data['message'].strip()
            if not user_message:
                return jsonify({'success': False, 'error': 'Message cannot be empty'}), 400
            
            # Set active conversation for this session
            session_id = session.get('session_id') or str(os.urandom(16).hex())
            session['session_id'] = session_id
            
            # Add message to queue for processing
            message_id = message_queue.add_message(conversation_id, session_id, user_message)
            
            # Return immediately with queue ID
            return jsonify({
                'success': True,
                'conversation_id': conversation_id,
                'message_id': message_id,
                'status': 'queued',
                'message': 'Your message has been queued for processing'
            })
            
        except Exception as e:
            logger.error(f"Error queuing message: {e}")
            return jsonify({
                'success': False, 
                'error': f'Error queuing message: {str(e)}'
            }), 500
    
    # Queue Management
    @app.route('/api/messages/<message_id>/status', methods=['GET'])
    def get_message_status(message_id):
        """Get the status of a queued message."""
        try:
            message_status = message_queue.get_message_status(message_id)
            if not message_status:
                return jsonify({'success': False, 'error': 'Message not found'}), 404
            
            response = {
                'success': True,
                'message_id': message_id,
                'status': message_status.status.value,
                'conversation_id': message_status.conversation_id,
                'timestamp': message_status.timestamp
            }
            
            if message_status.status == MessageStatus.COMPLETED and message_status.result:
                response['result'] = message_status.result
            elif message_status.status == MessageStatus.FAILED and message_status.error:
                response['error'] = message_status.error
                
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error getting message status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/queue/status', methods=['GET'])
    def get_queue_status():
        """Get information about the message queue."""
        try:
            queue_info = message_queue.get_queue_info()
            return jsonify({
                'success': True,
                'queue_info': queue_info
            })
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500


def process_message(conversation_id: str, session_id: str, user_message: str) -> Dict[str, Any]:
    """
    Process a message - this function is called by the queue worker.
    
    Args:
        conversation_id: ID of the conversation
        session_id: Session ID of the user
        user_message: The user's message to process
        
    Returns:
        Dict containing the processing result
        
    Raises:
        Exception: If processing fails
    """
    try:
        # Check if conversation exists, if not create a new one
        conversation = conversation_manager.get_conversation(conversation_id)
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found, creating new one")
            conversation_id = conversation_manager.create_conversation(
                title="Recovered Conversation", 
                session_id=session_id
            )
        else:
            conversation_manager.set_active_conversation(session_id, conversation_id)
        
        # Add user message to conversation
        user_message_id = conversation_manager.add_message(
            conversation_id=conversation_id,
            message_type='user',
            content=user_message
        )
        
        logger.info(f"Processing conversational question: {user_message}")
        
        # Get conversation context for Genie
        context = conversation_manager.get_context_for_genie(conversation_id, context_limit=3)
        contextual_question = f"{context}{user_message}" if context else user_message
        
        logger.info("Querying Databricks Genie with context...")
        
        # Query Genie with context
        genie_result = genie_client.query_data(contextual_question)
        
        # Process the response based on type
        if genie_result.data and genie_result.columns:
            return _process_chart_response(
                conversation_id, user_message_id, user_message, genie_result
            )
        elif genie_result.raw_response:
            return _process_text_response(
                conversation_id, user_message_id, user_message, genie_result
            )
        else:
            return _process_mock_response(
                conversation_id, user_message_id, user_message
            )
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        # Add error message to conversation
        conversation_manager.add_message(
            conversation_id=conversation_id,
            message_type='assistant_error',
            content=f"I encountered an error: {str(e)}",
            metadata={'error': str(e)}
        )
        raise Exception(f'Error processing question: {str(e)}')


def _process_chart_response(conversation_id: str, user_message_id: str, 
                          user_message: str, genie_result) -> Dict[str, Any]:
    """Process a response that contains tabular data for chart generation."""
    logger.info("Genie returned tabular data. Proceeding with chart generation.")
    
    # Get AI data summary
    logger.info("Getting data summary...")
    ai_summary = chatgpt_client.get_data_summary(
        data=genie_result.data, 
        columns=genie_result.columns,
        question=user_message
    )
    
    # Get visualization recommendation
    logger.info("Getting visualization recommendation...")
    chart_recommendation = chatgpt_client.recommend_visualization(
        data=genie_result.data, 
        columns=genie_result.columns,
        question=user_message
    )
    
    # Generate chart configuration
    logger.info("Generating chart configuration...")
    chart_config = viz_engine.create_chart_config(
        data=genie_result.data,
        columns=genie_result.columns,
        chart_type=chart_recommendation.chart_type,
        title=user_message
    )
    
    # Add assistant message with chart data
    assistant_message_id = conversation_manager.add_message(
        conversation_id=conversation_id,
        message_type='assistant_chart',
        content=ai_summary,
        metadata={
            'chart_config': chart_config,
            'ai_summary': ai_summary,
            'chart_reasoning': chart_recommendation.reasoning,
            'chart_type': chart_recommendation.chart_type,
            'sql_query': genie_result.sql_query,
            'data': genie_result.data[:10],  # Limit data in metadata
            'columns': genie_result.columns,
            'response_type': 'chart',
            'is_mock_data': False
        }
    )
    
    return {
        'success': True,
        'conversation_id': conversation_id,
        'user_message_id': user_message_id,
        'assistant_message_id': assistant_message_id,
        'response_type': 'chart',
        'content': ai_summary,
        'chart_config': chart_config,
        'ai_summary': ai_summary,
        'chart_reasoning': chart_recommendation.reasoning,
        'chart_type': chart_recommendation.chart_type,
        'sql_query': genie_result.sql_query,
        'data': genie_result.data[:50],  # Send more data for display
        'columns': genie_result.columns,
        'is_mock_data': False
    }


def _process_text_response(conversation_id: str, user_message_id: str, 
                         user_message: str, genie_result) -> Dict[str, Any]:
    """Process a text-only response from Genie."""
    logger.info("Genie returned text-only response.")
    
    # Add assistant message with text response
    assistant_message_id = conversation_manager.add_message(
        conversation_id=conversation_id,
        message_type='assistant_text',
        content=genie_result.raw_response,
        metadata={
            'response_type': 'text',
            'sql_query': genie_result.sql_query
        }
    )
    
    return {
        'success': True,
        'conversation_id': conversation_id,
        'user_message_id': user_message_id,
        'assistant_message_id': assistant_message_id,
        'response_type': 'text',
        'content': genie_result.raw_response,
        'sql_query': genie_result.sql_query
    }


def _process_mock_response(conversation_id: str, user_message_id: str, 
                         user_message: str) -> Dict[str, Any]:
    """Process response using mock data for demonstration."""
    logger.info("No useful response from Genie. Using mock data for demonstration.")
    
    mock_data = _generate_mock_data(user_message)
    
    # Get AI summary for mock data
    ai_summary = chatgpt_client.get_data_summary(
        data=mock_data['data'], 
        columns=mock_data['columns'],
        question=user_message
    )
    
    # Get visualization recommendation for mock data
    chart_recommendation = chatgpt_client.recommend_visualization(
        data=mock_data['data'], 
        columns=mock_data['columns'],
        question=user_message
    )
    
    # Generate chart configuration for mock data
    chart_config = viz_engine.create_chart_config(
        data=mock_data['data'],
        columns=mock_data['columns'],
        chart_type=chart_recommendation.chart_type,
        title=user_message
    )
    
    # Add assistant message with mock chart data
    assistant_message_id = conversation_manager.add_message(
        conversation_id=conversation_id,
        message_type='assistant_chart',
        content=ai_summary,
        metadata={
            'chart_config': chart_config,
            'ai_summary': ai_summary,
            'chart_reasoning': chart_recommendation.reasoning,
            'chart_type': chart_recommendation.chart_type,
            'sql_query': None,
            'data': mock_data['data'],
            'columns': mock_data['columns'],
            'response_type': 'chart',
            'is_mock_data': True
        }
    )
    
    return {
        'success': True,
        'conversation_id': conversation_id,
        'user_message_id': user_message_id,
        'assistant_message_id': assistant_message_id,
        'response_type': 'chart',
        'content': ai_summary,
        'chart_config': chart_config,
        'ai_summary': ai_summary,
        'chart_reasoning': chart_recommendation.reasoning,
        'chart_type': chart_recommendation.chart_type,
        'sql_query': None,
        'data': mock_data['data'],
        'columns': mock_data['columns'],
        'is_mock_data': True
    }


def _generate_mock_data(question: str) -> Dict[str, Any]:
    """Generate mock data based on the question type for demonstration purposes."""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['product', 'sales', 'revenue']):
        # Product sales data
        products = ['iPhone 15', 'MacBook Pro', 'iPad Air', 'Apple Watch', 'AirPods Pro']
        sales = [random.randint(50000, 500000) for _ in products]
        return {'data': list(zip(products, sales)), 'columns': ['product_name', 'sales_amount']}
    
    elif any(word in question_lower for word in ['employee', 'staff', 'department']):
        # Department employee data
        departments = ['Engineering', 'Sales', 'Marketing', 'Support', 'HR']
        employees = [random.randint(10, 150) for _ in departments]
        return {'data': list(zip(departments, employees)), 'columns': ['department', 'employee_count']}
    
    elif any(word in question_lower for word in ['month', 'time', 'trend', 'year']):
        # Time-based data
        months = ['Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024']
        values = [random.randint(10000, 100000) for _ in months]
        return {'data': list(zip(months, values)), 'columns': ['month', 'revenue']}
    
    elif any(word in question_lower for word in ['region', 'country', 'location']):
        # Geographic data
        regions = ['North America', 'Europe', 'Asia Pacific', 'South America', 'Africa']
        values = [random.randint(1000, 50000) for _ in regions]
        return {'data': list(zip(regions, values)), 'columns': ['region', 'total_sales']}
    
    else:
        # Default data
        categories = ['Category A', 'Category B', 'Category C', 'Category D']
        values = [random.randint(100, 1000) for _ in categories]
        return {'data': list(zip(categories, values)), 'columns': ['category', 'value']}


def queue_status_callback(message_id: str, status: MessageStatus, 
                         result: Dict = None, error: str = None):
    """Callback function for queue status updates."""
    try:
        logger.info(f"Message {message_id} status changed to {status.value}")
        # Here you could emit websocket events or store notifications
        # For now, we just log the status change
    except Exception as e:
        logger.warning(f"Queue status callback error: {e}")
