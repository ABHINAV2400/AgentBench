from .custom_model_client import Model as CustomModelClient
from .openai_client import OpenAIModel as OpenAIClient
from .gpt4_client import GPT4Client

# Only import optional clients if available
try:
    from .claude_client import ClaudeClient
except ImportError:
    ClaudeClient = None

try:
    from .gemini_client import GeminiClient  
except ImportError:
    GeminiClient = None

__all__ = [
    'CustomModelClient',
    'OpenAIClient', 
    'GPT4Client'
]

# Add optional clients if available
if ClaudeClient:
    __all__.append('ClaudeClient')
if GeminiClient:
    __all__.append('GeminiClient')