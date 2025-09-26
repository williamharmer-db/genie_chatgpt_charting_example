"""
Example questions configuration for the Genie to Chart POC

This file contains predefined example questions that users can click on
to quickly test the application. Questions are organized by category
and can be easily modified or extended.

HOW TO ADD NEW QUESTIONS:
1. Add a new dictionary to EXAMPLE_QUESTIONS list below
2. Include: text, description, category, and expected chart_type
3. Restart the Flask server (python web_app.py)
4. Questions will appear immediately in the UI

CATEGORIES:
- sales: Sales-related questions
- time_series: Time-based trend questions  
- geographic: Location-based questions
- analysis: Analytical/calculation questions
- distribution: Proportion/distribution questions
- financial: Financial metrics and analysis
"""

from typing import List, Dict

# Example questions organized by category
EXAMPLE_QUESTIONS = [
    {
        "text": "What are the top 5 products by total sales?",
        "description": "Top Products by Sales",
        "category": "sales",
        "chart_type": "bar"
    },
    {
        "text": "Show me revenue by month for the last year",
        "description": "Revenue by Month",
        "category": "time_series",
        "chart_type": "line"
    },
    {
        "text": "Which regions have the highest customer counts?",
        "description": "Customers by Region",
        "category": "geographic",
        "chart_type": "bar"
    },
    {
        "text": "What is the average order value by product category?",
        "description": "Average Order Value",
        "category": "analysis",
        "chart_type": "bar"
    },
    {
        "text": "Show me sales distribution by product category",
        "description": "Sales Distribution",
        "category": "distribution",
        "chart_type": "pie"
    },
    {
        "text": "What are quarterly revenue trends?",
        "description": "Quarterly Trends",
        "category": "time_series",
        "chart_type": "line"
    }
]

# Additional question sets for different industries or use cases
ADVANCED_QUESTIONS = [
    {
        "text": "Analyze customer retention rates by segment",
        "description": "Customer Retention Analysis",
        "category": "analytics",
        "chart_type": "bar"
    },
    {
        "text": "Show profit margins by product line over time",
        "description": "Profit Margin Trends",
        "category": "financial",
        "chart_type": "line"
    },
    {
        "text": "Compare year-over-year growth by department",
        "description": "YoY Growth Comparison",
        "category": "growth",
        "chart_type": "bar"
    }
]

def get_example_questions(category: str = None, limit: int = None) -> List[Dict]:
    """
    Get example questions, optionally filtered by category and limited in number
    
    Args:
        category: Filter questions by category (sales, time_series, geographic, etc.)
        limit: Maximum number of questions to return
        
    Returns:
        List of question dictionaries
    """
    questions = EXAMPLE_QUESTIONS.copy()
    
    if category:
        questions = [q for q in questions if q.get("category") == category]
    
    if limit:
        questions = questions[:limit]
        
    return questions

def get_all_categories() -> List[str]:
    """Get all unique categories from the example questions"""
    categories = set()
    for question in EXAMPLE_QUESTIONS:
        if "category" in question:
            categories.add(question["category"])
    return sorted(list(categories))

def add_custom_question(text: str, description: str, category: str = "custom", chart_type: str = "bar") -> Dict:
    """
    Helper function to create a new question dictionary
    
    Args:
        text: The question text
        description: Short description for the button
        category: Question category
        chart_type: Expected chart type (bar, line, pie)
        
    Returns:
        Question dictionary
    """
    return {
        "text": text,
        "description": description,
        "category": category,
        "chart_type": chart_type
    }

# Simple list format for backwards compatibility
SIMPLE_QUESTIONS = [q["text"] for q in EXAMPLE_QUESTIONS[:4]]  # First 4 for main UI
