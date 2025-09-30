"""
ChatGPT client for visualization recommendations using Azure OpenAI
"""
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from openai import AzureOpenAI
from loguru import logger
from ..core.config import settings


@dataclass
class ChartSpecification:
    """Chart specification for JavaScript charting library"""
    chart_type: str  # bar, line, pie, scatter, etc.
    title: str
    x_axis: Dict[str, Any]
    y_axis: Dict[str, Any]
    data: List[Dict[str, Any]]
    config: Dict[str, Any]  # Additional chart configuration
    library: str  # Chart.js, D3, etc.
    reasoning: str  # Why this visualization was chosen


class ChatGPTClient:
    """Client for getting visualization recommendations from Azure OpenAI"""
    
    def __init__(self, azure_endpoint: Optional[str] = None, 
                 azure_api_key: Optional[str] = None, azure_deployment: Optional[str] = None):
        
        # Use Azure OpenAI
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint or settings.azure_openai_endpoint,
            api_key=azure_api_key or settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version
        )
        self.model = azure_deployment or settings.azure_openai_deployment
        logger.info(f"Using Azure OpenAI with deployment: {self.model}")
    
    def get_data_summary(
        self,
        data: List[List[Any]], 
        columns: List[str], 
        question: str
    ) -> str:
        """
        Get a data summary from Azure OpenAI GPT-5
        """
        try:
            logger.info("Getting data summary from Azure OpenAI GPT-5")
            
            # Prepare data sample for analysis (limit to first 10 rows for summary)
            data_sample = data[:10] if len(data) > 10 else data
            
            # Create enhanced prompt for professional data analysis
            prompt = f"""You are a senior data analyst with expertise in business intelligence and statistical analysis. 
Analyze the following dataset and provide a professional data analysis summary.

CONTEXT:
Question: {question}
Data columns: {columns}
Total rows: {len(data)}
Sample data: {data_sample}

ANALYSIS REQUIREMENTS:
As a data analyst, please provide a 3-4 sentence analysis that includes:

1. KEY FINDINGS: What are the most significant insights from this data?
2. PATTERNS & TRENDS: Identify any notable patterns, trends, or outliers
3. BUSINESS IMPLICATIONS: What do these findings mean for decision-making?
4. DATA QUALITY: Comment on the data completeness and reliability

Write your analysis in a professional, actionable tone that would be suitable for a business stakeholder presentation. Focus on insights that drive business value and strategic thinking."""
            
            # Call Azure OpenAI API with enhanced analyst context
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior data analyst with 10+ years of experience in business intelligence, statistical analysis, and data storytelling. You provide clear, actionable insights that drive business decisions."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the response content
            summary = response.choices[0].message.content.strip()
            
            logger.info(f"GPT-5 data summary: {summary}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Azure OpenAI summary request failed: {e}")
            # Fallback summary
            return f"The data contains {len(data)} records with {len(columns)} columns: {', '.join(columns)}. This analysis addresses the question: {question}"

    def recommend_visualization(
        self, 
        data: List[List[Any]], 
        columns: List[str], 
        question: str,
        sql_query: str = ""
    ) -> ChartSpecification:
        """
        Get visualization recommendation from Azure OpenAI GPT-5
        """
        try:
            logger.info("Getting visualization recommendation from Azure OpenAI GPT-5")
            
            # Prepare data sample for analysis (limit to first 5 rows for GPT-5)
            data_sample = data[:5] if len(data) > 5 else data
            
            # Create enhanced data analyst prompt for chart recommendation
            prompt = f"""You are a senior data visualization specialist and business intelligence analyst.

DATASET ANALYSIS:
- Columns: {columns}
- Total rows: {len(data)}
- Question: {question}
- Sample data: {data_sample}

TASK: As a data analyst, recommend the most effective chart type for this business question.

Consider these factors:
1. Data type and structure
2. Business audience and decision-making context
3. Visual clarity and impact
4. Best practices in data visualization

Recommend ONE chart type (bar, line, or pie) and provide a clear business-focused explanation in 1-2 sentences about why this visualization will best serve stakeholders and drive insights."""
            
            # Call Azure OpenAI API with enhanced visualization analyst context
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior data visualization specialist and business intelligence expert. You understand both technical visualization principles and business communication needs. You recommend charts that maximize clarity, impact, and decision-making value."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the response content
            response_content = response.choices[0].message.content.strip()
            
            logger.info(f"GPT-5 response: {response_content}")
            
            # Parse the response to extract chart type and reasoning
            response_lower = response_content.lower()
            
            # Determine chart type from response
            if 'bar' in response_lower and ('line' not in response_lower or response_lower.index('bar') < response_lower.index('line')):
                chart_type = "bar"
            elif 'line' in response_lower and ('pie' not in response_lower or response_lower.index('line') < response_lower.index('pie')):
                chart_type = "line"
            elif 'pie' in response_lower:
                chart_type = "pie"
            else:
                # Default fallback based on question analysis
                if any(word in question.lower() for word in ['top', 'highest', 'best', 'most', 'rank']):
                    chart_type = "bar"
                elif any(word in question.lower() for word in ['trend', 'over time', 'by month', 'by year']):
                    chart_type = "line" 
                else:
                    chart_type = "bar"
            
            # Create title from question
            title = question.replace("?", "") if "?" in question else f"Analysis: {question}"
            
            # Use GPT-5's reasoning or create intelligent reasoning
            reasoning = response_content if response_content else f"{chart_type.title()} chart recommended for this data analysis"
            
            logger.info(f"Selected chart type: {chart_type}, reasoning: {reasoning}")
            
            return self._create_fallback_chart(data, columns, title, chart_type, reasoning)
            
        except Exception as e:
            logger.error(f"Azure OpenAI request failed: {e}")
            # Only use fallback when API actually fails
            return self._create_smart_chart(data, columns, question, sql_query)
    
    def _create_smart_chart(
        self, 
        data: List[List[Any]], 
        columns: List[str], 
        question: str,
        sql_query: str = ""
    ) -> ChartSpecification:
        """Create an intelligent chart based on data analysis"""
        
        # Analyze the question and data to determine best chart type
        question_lower = question.lower()
        
        # Smart chart type selection
        if any(word in question_lower for word in ['top', 'highest', 'best', 'most', 'rank']):
            chart_type = "bar"
            reasoning = "Bar chart is ideal for comparing and ranking values"
        elif any(word in question_lower for word in ['trend', 'over time', 'by month', 'by year', 'timeline']):
            chart_type = "line"
            reasoning = "Line chart is perfect for showing trends over time"
        elif any(word in question_lower for word in ['distribution', 'breakdown', 'percentage', 'share']):
            chart_type = "pie"
            reasoning = "Pie chart effectively shows distribution and proportions"
        elif len(columns) <= 2 and len(data) <= 10:
            chart_type = "bar"
            reasoning = "Bar chart works well for small datasets with clear categories"
        else:
            chart_type = "bar"
            reasoning = "Bar chart is versatile and works well for most data comparisons"
        
        # Create title based on question
        if "?" in question:
            title = question.replace("?", "")
        else:
            title = f"Analysis: {question}"
        
        return self._create_fallback_chart(data, columns, title, chart_type, reasoning)
    
    def _create_fallback_chart(
        self, 
        data: List[List[Any]], 
        columns: List[str], 
        question: str,
        chart_type: str = "bar",
        reasoning: str = "Chart created using intelligent fallback logic"
    ) -> ChartSpecification:
        """Create a chart with specified type and reasoning"""
        
        # Prepare data for Chart.js format
        chart_data = []
        if len(columns) >= 2 and data:
            # Use first two columns
            for row in data:
                # Convert value to float, handling string numbers from Databricks
                try:
                    value = float(str(row[1]).replace(',', '')) if row[1] is not None else 0
                except (ValueError, TypeError):
                    value = 0
                    
                chart_data.append({
                    "label": str(row[0]),
                    "value": value
                })
        elif len(columns) == 1 and data:
            # Single column - create labels with indices
            for i, row in enumerate(data):
                try:
                    value = float(str(row[0]).replace(',', '')) if row[0] is not None else i+1
                except (ValueError, TypeError):
                    value = i+1
                    
                chart_data.append({
                    "label": f"Item {i+1}",
                    "value": value
                })
        
        return ChartSpecification(
            chart_type=chart_type,
            title=question,
            x_axis={
                "label": columns[0] if columns else "Categories",
                "type": "category",
                "field": columns[0] if columns else "label"
            },
            y_axis={
                "label": columns[1] if len(columns) > 1 else "Values",
                "type": "linear", 
                "field": columns[1] if len(columns) > 1 else "value"
            },
            data=chart_data,
            config={
                "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"],
                "borderColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"],
                "responsive": True,
                "plugins": {
                    "legend": {"display": True},
                    "tooltip": {"enabled": True}
                }
            },
            library="Chart.js",
            reasoning=reasoning
        )

