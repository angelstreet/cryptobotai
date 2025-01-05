from enum import Enum
from typing import Dict, Any
from openai import OpenAI

class LLMProvider(Enum):
    OPENROUTER = "openrouter"
    # Add other providers if needed

class LLMService:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client

    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{
                    "role": "system",
                    "content": "You are a trading assistant that analyzes market data and provides trading decisions."
                },
                {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=500
            )
            
            # Debug print
            print("Raw API Response:", response)
            
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                return {
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "usage": response.usage
                }
            else:
                print("Invalid response structure:", response)
                return {
                    "content": "Error: Invalid response structure from API",
                    "model": None,
                    "usage": None
                }
                
        except Exception as e:
            print(f"Detailed error in generate_response: {str(e)}")
            return {
                "content": f"Error generating response: {str(e)}",
                "model": None,
                "usage": None
            } 