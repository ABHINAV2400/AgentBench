import os
import google.generativeai as genai
from typing import Dict, Any, Optional, List

class GeminiClient:
    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def generate_response(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]:
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = self.model.generate_content(full_prompt)
            
            return {
                "response": response.text,
                "model": self.model_name,
                "usage": {
                    "input_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                    "output_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0
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
            # Gemini tool calling implementation would go here
            # For now, return standard response
            return self.generate_response(prompt, system_prompt)
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "model": self.model_name,
                "error": True
            }