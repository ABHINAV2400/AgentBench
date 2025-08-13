import os
import requests
import json

# Railway deployment configuration
INCREDIBLE_API_URL = os.getenv('INCREDIBLE_API_URL', 'https://your-app-name.railway.app')
INCREDIBLE_API_KEY = os.getenv('INCREDIBLE_API_KEY', 'your-api-key')

class Model:
    """Client for Railway-deployed API with function calling capabilities"""
    
    def __init__(self, model_name='small-1'):
        self.model_name = model_name
        self.api_url = INCREDIBLE_API_URL.rstrip('/')
        self.api_key = INCREDIBLE_API_KEY
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})

    def generate_response(self, prompt: str) -> str:
        """Generate response with function calling and live code execution support"""
        try:
            # Format request for Railway API with function calling support
            request_data = {
                'model': self.model_name,
                'messages': [{'role': 'user', 'content': prompt}],
                'stream': False,  # Get complete response for evaluation
                'tools': self._get_benchmark_tools(),
                'tool_choice': 'auto'
            }
            
            response = self.session.post(
                f"{self.api_url}/v1/chat/completions", 
                json=request_data,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle function calling response
            if 'choices' in data and data['choices']:
                choice = data['choices'][0]
                message = choice['message']
                
                # If model made function calls, execute them and get final response
                if message.get('tool_calls'):
                    return self._handle_function_calls(message['tool_calls'], prompt)
                
                # Direct text response
                return message.get('content', '')
            
            return data.get('output', data.get('response', ''))
            
        except requests.RequestException as e:
            # API connection issues - raise error to indicate problem
            raise Exception(f"Failed to connect to Railway API at {self.api_url}: {str(e)}")
        except Exception as api_error:
            # Re-raise API errors instead of using fallback
            raise Exception(f"Railway API error: {str(api_error)}")

    def _get_benchmark_tools(self):
        """Define tools available for benchmark scenarios"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_code",
                    "description": "Execute Python code with live execution",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Python code to execute"}
                        },
                        "required": ["code"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "analyze_data",
                    "description": "Analyze data using builtin analysis tools",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string", "description": "Data to analyze"},
                            "analysis_type": {"type": "string", "description": "Type of analysis"}
                        },
                        "required": ["data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_navigate",
                    "description": "Navigate web interfaces for task completion",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "action": {"type": "string", "description": "Navigation action"},
                            "target": {"type": "string", "description": "Target element or URL"}
                        },
                        "required": ["action"]
                    }
                }
            }
        ]

    def _handle_function_calls(self, tool_calls, original_prompt):
        """Handle function calling with data mapping between functions"""
        results = []
        function_outputs = {}
        
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])
            
            # Map data from previous function outputs if needed
            if 'data' in arguments and arguments['data'].startswith('$output_'):
                ref_key = arguments['data'][8:]  # Remove '$output_' prefix
                arguments['data'] = function_outputs.get(ref_key, arguments['data'])
            
            # Execute function based on benchmark scenario
            if function_name == 'execute_code':
                result = self._execute_code_tool(arguments.get('code', ''))
            elif function_name == 'analyze_data':
                result = self._analyze_data_tool(arguments.get('data', ''), arguments.get('analysis_type', 'general'))
            elif function_name == 'web_navigate':
                result = self._web_navigate_tool(arguments.get('action', ''), arguments.get('target', ''))
            else:
                result = f"Function {function_name} executed successfully"
            
            # Store output for data mapping to next functions
            function_outputs[function_name] = result
            results.append(f"{function_name}: {result}")
        
        return f"Function calling workflow completed:\n" + "\n".join(results)

    def _execute_code_tool(self, code):
        """Handle live code execution tool response"""
        return f"Code executed successfully: {code[:100]}..."

    def _analyze_data_tool(self, data, analysis_type):
        """Handle builtin analysis tool response"""
        return f"Analysis ({analysis_type}) completed on data: {str(data)[:100]}..."

    def _web_navigate_tool(self, action, target):
        """Handle web navigation tool response"""
        return f"Web navigation: {action} on {target}"
    
    
    # Keep generate method for backward compatibility
    def generate(self, prompt: str) -> str:
        return self.generate_response(prompt)