import os
import anthropic
from typing import Dict, Any, Optional, List

class ClaudeClient:
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model_name = model_name
        self.max_tokens = 4096

    def generate_response(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]:
        try:
            messages = []
            if prompt:
                messages.append({"role": "user", "content": prompt})
                
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                system=system_prompt if system_prompt else "You are a helpful AI assistant.",
                messages=messages
            )
            
            return {
                "response": response.content[0].text,
                "model": self.model_name,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "model": self.model_name,
                "error": True
            }

    def generate_with_tools(self, prompt: str, tools: List[Dict], system_prompt: str = "") -> Dict[str, Any]:
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                system=system_prompt if system_prompt else "You are a helpful AI assistant that can use tools.",
                messages=messages,
                tools=tools
            )
            
            return {
                "response": response.content[0].text if response.content[0].type == "text" else "",
                "tool_calls": [block for block in response.content if block.type == "tool_use"],
                "model": self.model_name,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "model": self.model_name,
                "error": True
            }