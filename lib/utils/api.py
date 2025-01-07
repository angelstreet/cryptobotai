import os
import requests
from openai import OpenAI
from anthropic import Anthropic

def get_ai_credentials():
    """Get credentials for the selected AI provider"""
    provider = os.getenv("AI_PROVIDER", "OPENAI").upper()
    
    # Get provider-specific settings
    credentials = {
        "api_key": os.getenv(f"{provider}_API_KEY"),
        "base_url": os.getenv(f"{provider}_API_URL"),
        "model": os.getenv(f"{provider}_MODEL"),
        "temperature": float(os.getenv(f"{provider}_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv(f"{provider}_MAX_TOKENS", "200")),
        "headers": {}
    }
    
    # Handle OpenRouter specific configuration
    if provider == "OPENROUTER":
        credentials["model"] = os.getenv("AI_MODEL")
        credentials["headers"].update({
            "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),
            "X-Title": os.getenv("APP_NAME", "Crypto AI Trading Bot")
        })
    
    if provider == "OPENAI":
        credentials["model"] = os.getenv("OPENAI_MODEL")
    
    return credentials

class OllamaLLM:
    """Wrapper for Ollama API that mimics OpenAI interface"""
    def __init__(self, base_url):
        self.base_url = base_url
        
    def chat_completions_create(self, **kwargs):
        # Convert OpenAI format to Ollama format
        messages = kwargs.get('messages', [])
        prompt = "\n".join([m["content"] for m in messages])
        
        # Ollama parameters
        # https://github.com/ollama/ollama/blob/main/docs/api.md#parameters
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": kwargs.get('model', 'llama2'),
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 100,  # Similar to max_tokens
                    "top_p": 0.9,       # Alternative to temperature
                    "stop": ["</response>", "Action:"]  # Stop sequences
                }
            }
        )
        
        # Convert Ollama response to OpenAI format
        result = response.json()
        return {
            "choices": [{
                "message": {
                    "content": result.get('response', '')
                }
            }]
        }

def get_ai_client(creds):
    """Get the appropriate AI client based on provider"""
    provider = os.getenv("AI_PROVIDER", "OPENAI").upper()
    
    if provider == "LOCAL":
        return OllamaLLM(creds["base_url"])
    elif provider == "CLAUDE":
        return Anthropic(api_key=creds["api_key"])
    else:
        return OpenAI(
            api_key=creds["api_key"],
            base_url=creds["base_url"],
            default_headers=creds["headers"],
            timeout=30.0
        ) 