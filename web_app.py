"""
Flask web application for the Genie to Chart POC with React frontend
"""
import os
import json
import random
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from loguru import logger
from genie_client import GenieClient, GenieQueryResult
from chatgpt_client import ChatGPTClient
from visualization_engine import VisualizationEngine
from example_questions import get_example_questions


app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)  # Enable CORS for all routes


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
    print("🌐 Open http://localhost:5000 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

