"""
Visualization engine for converting chart specifications to JavaScript charts
"""
import json
from typing import Dict, List, Any
from dataclasses import asdict
from loguru import logger
from chatgpt_client import ChartSpecification


class VisualizationEngine:
    """Engine for generating JavaScript chart configurations"""
    
    def __init__(self):
        pass
    
    def generate_chartjs_config(self, spec: ChartSpecification) -> Dict[str, Any]:
        """Generate a complete Chart.js configuration from a chart specification"""
        try:
            # Base Chart.js configuration
            config = {
                "type": spec.chart_type,
                "data": self._prepare_chartjs_data(spec),
                "options": self._prepare_chartjs_options(spec)
            }
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to generate Chart.js config: {e}")
            raise
    
    def _prepare_chartjs_data(self, spec: ChartSpecification) -> Dict[str, Any]:
        """Prepare data section for Chart.js"""
        
        if spec.chart_type in ["pie", "doughnut", "polarArea"]:
            # For pie charts, data format is different
            labels = [item["label"] for item in spec.data]
            data_values = [item["value"] for item in spec.data]
            
            return {
                "labels": labels,
                "datasets": [{
                    "data": data_values,
                    "backgroundColor": spec.config.get("backgroundColor", ["#FF6384", "#36A2EB", "#FFCE56"]),
                    "borderColor": spec.config.get("borderColor", ["#FF6384", "#36A2EB", "#FFCE56"]),
                    "borderWidth": 1
                }]
            }
        
        elif spec.chart_type in ["bar", "line", "scatter", "bubble"]:
            # For bar/line charts
            labels = [item["label"] for item in spec.data]
            data_values = [item["value"] for item in spec.data]
            
            dataset_config = {
                "label": spec.title,
                "data": data_values,
                "backgroundColor": spec.config.get("backgroundColor", "#36A2EB"),
                "borderColor": spec.config.get("borderColor", "#36A2EB"),
                "borderWidth": 1
            }
            
            # Additional configuration for line charts
            if spec.chart_type == "line":
                dataset_config["fill"] = False
                dataset_config["tension"] = 0.1
            
            return {
                "labels": labels,
                "datasets": [dataset_config]
            }
        
        else:
            # Fallback for other chart types
            labels = [item["label"] for item in spec.data]
            data_values = [item["value"] for item in spec.data]
            
            return {
                "labels": labels,
                "datasets": [{
                    "data": data_values,
                    "backgroundColor": spec.config.get("backgroundColor", "#36A2EB")
                }]
            }
    
    def _prepare_chartjs_options(self, spec: ChartSpecification) -> Dict[str, Any]:
        """Prepare options section for Chart.js"""
        
        options = {
            "responsive": spec.config.get("responsive", True),
            "plugins": {
                "title": {
                    "display": True,
                    "text": spec.title
                },
                "legend": spec.config.get("plugins", {}).get("legend", {"display": True}),
                "tooltip": spec.config.get("plugins", {}).get("tooltip", {"enabled": True})
            }
        }
        
        # Add scales for charts that support them
        if spec.chart_type not in ["pie", "doughnut", "polarArea", "radar"]:
            options["scales"] = {
                "x": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": spec.x_axis.get("label", "X Axis")
                    }
                },
                "y": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": spec.y_axis.get("label", "Y Axis")
                    },
                    "type": spec.y_axis.get("type", "linear")
                }
            }
        
        return options
    
    def generate_html_page(self, spec: ChartSpecification, include_data_table: bool = True) -> str:
        """Generate a complete HTML page with the chart"""
        
        chart_config = self.generate_chartjs_config(spec)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{spec.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-container {{
            position: relative;
            height: 500px;
            margin: 20px 0;
        }}
        .info-section {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .data-table th, .data-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        .data-table th {{
            background-color: #f2f2f2;
        }}
        .reasoning {{
            font-style: italic;
            color: #666;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{spec.title}</h1>
        
        <div class="info-section">
            <h3>Chart Information</h3>
            <p><strong>Chart Type:</strong> {spec.chart_type.title()}</p>
            <p><strong>Library:</strong> {spec.library}</p>
            <div class="reasoning">
                <strong>Why this visualization:</strong> {spec.reasoning}
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="myChart"></canvas>
        </div>
        
        {self._generate_data_table_html(spec) if include_data_table else ""}
        
        <div class="info-section">
            <h3>Chart Configuration</h3>
            <details>
                <summary>Click to view Chart.js configuration</summary>
                <pre>{json.dumps(chart_config, indent=2)}</pre>
            </details>
        </div>
    </div>

    <script>
        const config = {json.dumps(chart_config, indent=2)};
        
        const ctx = document.getElementById('myChart').getContext('2d');
        const myChart = new Chart(ctx, config);
        
        // Log configuration for debugging
        console.log('Chart configuration:', config);
    </script>
</body>
</html>
"""
        return html_template
    
    def _generate_data_table_html(self, spec: ChartSpecification) -> str:
        """Generate HTML table showing the chart data"""
        
        if not spec.data:
            return ""
        
        table_html = """
        <div class="info-section">
            <h3>Data Used in Chart</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Label</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for item in spec.data:
            table_html += f"""
                    <tr>
                        <td>{item.get('label', 'N/A')}</td>
                        <td>{item.get('value', 'N/A')}</td>
                    </tr>
"""
        
        table_html += """
                </tbody>
            </table>
        </div>
"""
        
        return table_html
    
    def save_chart_html(self, spec: ChartSpecification, filename: str = "chart.html") -> str:
        """Save the chart as an HTML file and return the file path"""
        try:
            html_content = self.generate_html_page(spec)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Chart saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to save chart HTML: {e}")
            raise

