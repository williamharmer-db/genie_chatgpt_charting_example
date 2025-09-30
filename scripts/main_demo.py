"""
Genie to Chart POC - Main Demo Script
=====================================

This POC demonstrates:
1. Querying Databricks Genie API for data
2. Using ChatGPT to recommend the best visualization
3. Generating Chart.js specifications for JavaScript charts
4. Creating an interactive HTML page with the chart
"""

import os
import webbrowser
from typing import Optional
from loguru import logger
from genie_client import GenieClient
from chatgpt_client import ChatGPTClient
from visualization_engine import VisualizationEngine


class GenieToChartPOC:
    """Main POC class that orchestrates the entire flow"""
    
    def __init__(self):
        self.genie_client = GenieClient()
        self.chatgpt_client = ChatGPTClient()
        self.viz_engine = VisualizationEngine()
    
    def run_demo(self, question: str, output_file: Optional[str] = None) -> str:
        """
        Run the complete demo flow:
        1. Query Genie for data
        2. Get visualization recommendation from ChatGPT  
        3. Generate interactive chart
        4. Save as HTML file
        
        Returns the path to the generated HTML file
        """
        logger.info(f"🚀 Starting Genie to Chart POC for question: '{question}'")
        
        try:
            # Step 1: Query Genie for data
            logger.info("📊 Step 1: Querying Databricks Genie...")
            genie_result = self.genie_client.query_data(question)
            
            logger.info(f"✅ Genie query completed:")
            logger.info(f"   - SQL: {genie_result.sql_query}")
            logger.info(f"   - Columns: {genie_result.columns}")
            logger.info(f"   - Rows: {len(genie_result.data)}")
            
            if not genie_result.data:
                raise ValueError("No data returned from Genie query")
            
            # Step 2: Get visualization recommendation from ChatGPT
            logger.info("🤖 Step 2: Getting visualization recommendation from ChatGPT...")
            chart_spec = self.chatgpt_client.recommend_visualization(
                data=genie_result.data,
                columns=genie_result.columns,
                question=question,
                sql_query=genie_result.sql_query
            )
            
            logger.info(f"✅ ChatGPT recommendation received:")
            logger.info(f"   - Chart type: {chart_spec.chart_type}")
            logger.info(f"   - Title: {chart_spec.title}")
            logger.info(f"   - Reasoning: {chart_spec.reasoning}")
            
            # Step 3: Generate interactive chart
            logger.info("📈 Step 3: Generating interactive chart...")
            if not output_file:
                output_file = f"chart_{question.replace(' ', '_').replace('?', '').lower()}.html"
            
            html_file = self.viz_engine.save_chart_html(chart_spec, output_file)
            
            logger.info(f"✅ Chart generated and saved to: {html_file}")
            
            return html_file
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise
    
    def run_interactive_demo(self):
        """Run an interactive demo where user can ask multiple questions"""
        print("🚀 Genie to Chart POC - Interactive Demo")
        print("=" * 60)
        print("This demo will:")
        print("1. 📊 Query your data using Databricks Genie")
        print("2. 🤖 Ask ChatGPT for the best visualization approach")
        print("3. 📈 Generate an interactive Chart.js visualization")
        print("4. 🌐 Open the result in your web browser")
        print("-" * 60)
        
        # Check environment variables
        required_vars = ["DATABRICKS_HOST", "DATABRICKS_TOKEN", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print("❌ Missing required environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\nPlease set these environment variables or create a .env file:")
            print("DATABRICKS_HOST='https://your-workspace.cloud.databricks.com'")
            print("DATABRICKS_TOKEN='your-personal-access-token'")
            print("AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
            print("AZURE_OPENAI_API_KEY='your-azure-openai-api-key'")
            print("AZURE_OPENAI_DEPLOYMENT='your-deployment-name'")
            return
        
        print("✅ Environment configured")
        print(f"   - Databricks Host: {os.getenv('DATABRICKS_HOST')}")
        print(f"   - Azure OpenAI: Configured")
        space_id = os.getenv('GENIE_SPACE_ID')
        if space_id:
            print(f"   - Genie Space ID: {space_id}")
        else:
            print("   - Genie Space ID: Will use first available space")
        
        while True:
            try:
                print(f"\n💬 Ask a question about your data:")
                print("Examples:")
                print("  - 'What are the top 5 products by sales?'")
                print("  - 'Show me revenue by month'")
                print("  - 'Which customers have the highest order values?'")
                print("  - 'What is the sales performance by region?'")
                print("\nType 'quit', 'exit', or 'bye' to end the demo.")
                
                user_question = input("\n👤 Your question: ").strip()
                
                # Check for exit commands
                if user_question.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Goodbye! Thanks for trying the Genie to Chart POC.")
                    break
                
                if not user_question:
                    print("🤖 Please enter a question or type 'quit' to exit.")
                    continue
                
                # Run the demo
                print(f"\n🔄 Processing your question: '{user_question}'")
                print("This may take a moment...")
                
                html_file = self.run_demo(user_question)
                
                # Open in browser
                print(f"\n🌐 Opening chart in your default web browser...")
                file_path = os.path.abspath(html_file)
                webbrowser.open(f"file://{file_path}")
                
                print(f"✅ Demo completed successfully!")
                print(f"📄 Chart saved as: {html_file}")
                print(f"🔗 File path: {file_path}")
                
                # Ask if they want to continue
                continue_demo = input("\n❓ Would you like to ask another question? (y/n): ").strip().lower()
                if continue_demo not in ['y', 'yes', '']:
                    print("👋 Thanks for trying the Genie to Chart POC!")
                    break
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for trying the Genie to Chart POC.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Please try again or type 'quit' to exit.")


def run_sample_demo():
    """Run a predefined demo with sample questions"""
    poc = GenieToChartPOC()
    
    sample_questions = [
        "What are the top 5 products by total sales?",
        "Show me revenue by month for the last year",
        "Which regions have the highest customer counts?",
        "What is the average order value by product category?"
    ]
    
    print("🚀 Running Sample Demo with Predefined Questions")
    print("=" * 60)
    
    for i, question in enumerate(sample_questions, 1):
        try:
            print(f"\n📝 Sample Question {i}: {question}")
            html_file = poc.run_demo(question, f"sample_chart_{i}.html")
            print(f"✅ Chart {i} saved as: {html_file}")
            
        except Exception as e:
            print(f"❌ Sample {i} failed: {e}")
    
    print(f"\n🎉 Sample demo completed!")


def main():
    """Main entry point"""
    print("🚀 Genie to Chart POC")
    print("=" * 60)
    print("Choose a demo mode:")
    print("1. Interactive Demo - Ask your own questions")
    print("2. Sample Demo - Run predefined questions")
    
    while True:
        try:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            if choice == '1':
                poc = GenieToChartPOC()
                poc.run_interactive_demo()
                break
            elif choice == '2':
                run_sample_demo()
                break
            else:
                print("Please enter 1 or 2")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()

