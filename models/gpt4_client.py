import os
import openai
from typing import Dict, Any, Optional, List

class GPT4Client:
    def __init__(self, model_name: str = "gpt-4o"):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model_name = model_name

    def generate_response(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=4096
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": self.model_name,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
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
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools,
                max_tokens=4096
            )
            
            return {
                "response": response.choices[0].message.content or "",
                "tool_calls": response.choices[0].message.tool_calls or [],
                "model": self.model_name,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                }
            }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "model": self.model_name,
                "error": True
            }