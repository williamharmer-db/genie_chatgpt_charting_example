"""
Flask web application for the Genie to Chart POC with React frontend
"""
import os
import json
import random
from flask import Flask, request, jsonify, send_from_directory, send_file, session
from flask_cors import CORS
from loguru import logger
from genie_client import GenieClient, GenieQueryResult
from chatgpt_client import ChatGPTClient
from visualization_engine import VisualizationEngine
from example_questions import get_example_questions
from conversation_manager import conversation_manager
from message_queue import message_queue, MessageStatus


app = Flask(__name__, static_folder='frontend/build', static_url_path='')
app.secret_key = os.urandom(24)  # For session management
CORS(app, supports_credentials=True)  # Enable CORS with credentials for sessions


def generate_mock_data(question: str):
    """Generate mock data based on the question type for demonstration purposes"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['product', 'sales', 'revenue']):
        # Product sales data
        products = ['iPhone 15', 'MacBook Pro', 'iPad Air', 'Apple Watch', 'AirPods Pro']
        sales = [random.randint(50000, 500000) for _ in products]
        return list(zip(products, sales)), ['product_name', 'sales_amount']
    
    elif any(word in question_lower for word in ['employee', 'staff', 'department']):
        # Department employee data
        departments = ['Engineering', 'Sales', 'Marketing', 'Support', 'HR']
        employees = [random.randint(10, 150) for _ in departments]
        return list(zip(departments, employees)), ['department', 'employee_count']
    
    elif any(word in question_lower for word in ['month', 'time', 'trend', 'year']):
        # Time-based data
        months = ['Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024']
        values = [random.randint(10000, 100000) for _ in months]
        return list(zip(months, values)), ['month', 'revenue']
    
    elif any(word in question_lower for word in ['region', 'country', 'location']):
        # Geographic data
        regions = ['North America', 'Europe', 'Asia Pacific', 'South America', 'Africa']
        values = [random.randint(1000, 50000) for _ in regions]
        return list(zip(regions, values)), ['region', 'total_sales']
    
    else:
        # Default generic data
        categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
        values = [random.randint(100, 1000) for _ in categories]
        return list(zip(categories, values)), ['category', 'value']


class WebApp:
    """Web application wrapper for the Genie to Chart POC"""
    
    def __init__(self):
        self.genie_client = GenieClient()
        self.chatgpt_client = ChatGPTClient()
        self.viz_engine = VisualizationEngine()


web_poc = WebApp()


@app.route('/')
def index():
    """Serve React app"""
    try:
        return send_file('frontend/build/index.html')
    except FileNotFoundError:
        # Fallback to development message if React build doesn't exist
        return jsonify({
            'message': 'React frontend not built yet',
            'instructions': 'Run: cd frontend && npm run build'
        }), 404

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from React build"""
    return send_from_directory('frontend/build/static', filename)


@app.route('/api/query', methods=['POST'])
def query_data():
    """API endpoint to process a data query"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        logger.info(f"Processing question: {question}")
        
        # Step 1: Query Genie for data
        logger.info("Querying Databricks Genie...")
        genie_result = web_poc.genie_client.query_data(question)
        
        # Check what type of response we got from Genie
        has_tabular_data = genie_result.data and genie_result.columns and len(genie_result.data) > 0
        has_text_response = genie_result.raw_response and genie_result.raw_response.strip()
        
        if has_tabular_data:
            # We have tabular data - proceed with chart generation
            logger.info("Genie returned tabular data. Proceeding with chart generation.")
            
            # Step 2a: Get data summary from ChatGPT
            logger.info("Getting data summary...")
            data_summary_text = web_poc.chatgpt_client.get_data_summary(
                data=genie_result.data,
                columns=genie_result.columns,
                question=question
            )
            
            # Step 2b: Get visualization recommendation from ChatGPT
            logger.info("Getting visualization recommendation...")
            chart_spec = web_poc.chatgpt_client.recommend_visualization(
                data=genie_result.data,
                columns=genie_result.columns,
                question=question,
                sql_query=genie_result.sql_query
            )
            
            # Step 3: Generate Chart.js configuration
            logger.info("Generating chart configuration...")
            chart_config = web_poc.viz_engine.generate_chartjs_config(chart_spec)
            
            # Return chart response
            response = {
                'success': True,
                'response_type': 'chart',
                'question': question,
                'sql_query': genie_result.sql_query,
                'data_summary': {
                    'columns': genie_result.columns,
                    'row_count': len(genie_result.data),
                    'sample_data': genie_result.data[:5],  # First 5 rows for preview
                    'ai_summary': data_summary_text  # AI-generated summary
                },
                'chart_spec': {
                    'chart_type': chart_spec.chart_type,
                    'title': chart_spec.title,
                    'reasoning': chart_spec.reasoning,
                    'library': chart_spec.library
                },
                'chart_config': chart_config
            }
            
        elif has_text_response:
            # We have a text response but no tabular data - return text only
            logger.info("Genie returned text response only. Skipping chart generation.")
            
            response = {
                'success': True,
                'response_type': 'text',
                'question': question,
                'text_response': genie_result.raw_response.strip(),
                'sql_query': genie_result.sql_query if genie_result.sql_query else None
            }
            
        else:
            # No tabular data and no text response - use mock data for demonstration
            logger.warning("Genie returned no data or text. Using mock data for demonstration.")
            
            # Create mock data based on the question type
            mock_data, mock_columns = generate_mock_data(question)
            
            # Step 2a: Get data summary for mock data
            logger.info("Getting data summary for mock data...")
            mock_data_summary_text = web_poc.chatgpt_client.get_data_summary(
                data=mock_data,
                columns=mock_columns,
                question=question
            )
            
            # Step 2b: Get visualization recommendation from ChatGPT
            logger.info("Getting visualization recommendation for mock data...")
            chart_spec = web_poc.chatgpt_client.recommend_visualization(
                data=mock_data,
                columns=mock_columns,
                question=question,
                sql_query=f"-- Mock SQL for demonstration\nSELECT {', '.join(mock_columns)} FROM demo_table WHERE question = '{question}' LIMIT 5;"
            )
            
            # Step 3: Generate Chart.js configuration
            logger.info("Generating chart configuration for mock data...")
            chart_config = web_poc.viz_engine.generate_chartjs_config(chart_spec)
            
            # Return mock chart response
            response = {
                'success': True,
                'response_type': 'chart',
                'is_mock_data': True,
                'question': question,
                'sql_query': f"-- Mock SQL for demonstration\nSELECT {', '.join(mock_columns)} FROM demo_table WHERE question = '{question}' LIMIT 5;",
                'data_summary': {
                    'columns': mock_columns,
                    'row_count': len(mock_data),
                    'sample_data': mock_data[:5],  # First 5 rows for preview
                    'ai_summary': mock_data_summary_text  # AI-generated summary for mock data
                },
                'chart_spec': {
                    'chart_type': chart_spec.chart_type,
                    'title': chart_spec.title,
                    'reasoning': chart_spec.reasoning,
                    'library': chart_spec.library
                },
                'chart_config': chart_config
            }
        
        logger.info(f"Successfully processed question: {question}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if required environment variables are set
        required_vars = ["DATABRICKS_HOST", "DATABRICKS_TOKEN", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return jsonify({
                'status': 'error',
                'message': f'Missing environment variables: {", ".join(missing_vars)}'
            }), 500
        
        return jsonify({
            'status': 'healthy',
            'message': 'All systems operational',
            'configuration': {
                'databricks_host': os.getenv('DATABRICKS_HOST'),
                'genie_space_id': os.getenv('GENIE_SPACE_ID', 'auto-detect'),
                'azure_openai_configured': bool(os.getenv('AZURE_OPENAI_API_KEY'))
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/example-questions')
def get_example_questions_api():
    """Get example questions for the frontend"""
    try:
        # Get the first 4 questions for the main UI (backwards compatibility)
        questions = get_example_questions(limit=4)
        
        # Convert to the format expected by the frontend
        frontend_questions = []
        for q in questions:
            frontend_questions.append({
                'text': q['text'],
                'description': q['description']
            })
        
        return jsonify({
            'success': True,
            'questions': frontend_questions,
            'total_available': len(get_example_questions())
        })
    except Exception as e:
        logger.error(f"Error loading example questions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations for the sidebar"""
    try:
        conversations = conversation_manager.get_all_conversations(limit=20)
        return jsonify({
            'success': True,
            'conversations': conversations
        })
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation"""
    try:
        data = request.get_json() or {}
        title = data.get('title')
        session_id = session.get('session_id') or str(os.urandom(16).hex())
        session['session_id'] = session_id
        
        conversation_id = conversation_manager.create_conversation(title=title, session_id=session_id)
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'session_id': session_id
        })
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation with all messages"""
    try:
        conversation = conversation_manager.get_conversation(conversation_id)
        if not conversation:
            # If conversation doesn't exist, create a new one
            logger.warning(f"Conversation {conversation_id} not found, creating new one")
            new_conversation_id = conversation_manager.create_conversation(title="New Conversation")
            conversation = conversation_manager.get_conversation(new_conversation_id)
            
            return jsonify({
                'success': True,
                'conversation': conversation.to_dict(),
                'new_conversation_id': new_conversation_id
            })
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict()
        })
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def process_message(conversation_id: str, session_id: str, user_message: str) -> dict:
    """Process a message - this function is called by the queue worker"""
    try:
        # Check if conversation exists, if not create a new one
        conversation = conversation_manager.get_conversation(conversation_id)
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found, creating new one")
            conversation_id = conversation_manager.create_conversation(title="Recovered Conversation", session_id=session_id)
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
        genie_result = web_poc.genie_client.query_data(contextual_question)
        
        # Process the response based on type
        if genie_result.data and genie_result.columns:
            # Tabular data - generate chart and summary
            logger.info("Genie returned tabular data. Proceeding with chart generation.")
            
            # Get AI data summary
            logger.info("Getting data summary...")
            ai_summary = web_poc.chatgpt_client.get_data_summary(
                data=genie_result.data, 
                columns=genie_result.columns,
                question=user_message
            )
            
            # Get visualization recommendation
            logger.info("Getting visualization recommendation...")
            chart_recommendation = web_poc.chatgpt_client.recommend_visualization(
                data=genie_result.data, 
                columns=genie_result.columns,
                question=user_message
            )
            
            # Generate chart configuration
            logger.info("Generating chart configuration...")
            chart_config = web_poc.viz_engine.create_chart_config(
                data=genie_result.data,
                columns=genie_result.columns,
                chart_type=chart_recommendation.chart_type,
                title=user_message
            )
            
            # Add assistant message with chart data
            assistant_message_id = conversation_manager.add_message(
                conversation_id=conversation_id,
                message_type='assistant_chart',
                content=ai_summary,  # Use AI summary as main content
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
            
            response_data = {
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
            
        elif genie_result.raw_response:
            # Text-only response
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
            
            response_data = {
                'success': True,
                'conversation_id': conversation_id,
                'user_message_id': user_message_id,
                'assistant_message_id': assistant_message_id,
                'response_type': 'text',
                'content': genie_result.raw_response,
                'sql_query': genie_result.sql_query
            }
            
        else:
            # No useful response - use mock data for demo
            logger.info("No useful response from Genie. Using mock data for demonstration.")
            
            mock_data = generate_mock_data(user_message)
            
            # Get AI summary for mock data
            ai_summary = web_poc.chatgpt_client.get_data_summary(
                data=mock_data['data'], 
                columns=mock_data['columns'],
                question=user_message
            )
            
            # Get visualization recommendation for mock data
            chart_recommendation = web_poc.chatgpt_client.recommend_visualization(
                data=mock_data['data'], 
                columns=mock_data['columns'],
                question=user_message
            )
            
            # Generate chart configuration for mock data
            chart_config = web_poc.viz_engine.create_chart_config(
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
            
            response_data = {
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
        
        logger.info(f"Successfully processed conversational question: {user_message}")
        return response_data
        
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


@app.route('/api/conversations/<conversation_id>/messages', methods=['POST'])
def add_message_to_conversation(conversation_id):
    """Add a message to a conversation queue for processing"""
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


@app.route('/api/messages/<message_id>/status', methods=['GET'])
def get_message_status(message_id):
    """Get the status of a queued message"""
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
    """Get information about the message queue"""
    try:
        queue_info = message_queue.get_queue_info()
        return jsonify({
            'success': True,
            'queue_info': queue_info
        })
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        conversation_manager.delete_conversation(conversation_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Initialize and configure the message queue
def queue_status_callback(message_id: str, status: MessageStatus, result: dict = None, error: str = None):
    """Callback function for queue status updates"""
    try:
        logger.info(f"Message {message_id} status changed to {status.value}")
        # Here you could emit websocket events or store notifications
        # For now, we just log the status change
    except Exception as e:
        logger.warning(f"Queue status callback error: {e}")


# Set up the message queue
message_queue.set_message_processor(process_message)
message_queue.set_status_callback(queue_status_callback)


if __name__ == '__main__':
    # Check environment setup
    required_vars = ["DATABRICKS_HOST", "DATABRICKS_TOKEN", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables or create a .env file")
        exit(1)
    
    print("🚀 Starting Genie to Chart POC Web App")
    print(f"📊 Databricks: {os.getenv('DATABRICKS_HOST')}")
    print(f"🤖 OpenAI: Configured")
    print("📬 Starting message queue...")
    
    # Start the message queue
    message_queue.start()
    
    print("🌐 Open http://localhost:5000 in your browser")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        # Clean shutdown of the message queue
        print("📬 Stopping message queue...")
        message_queue.stop()

