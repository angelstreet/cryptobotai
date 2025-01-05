from decimal import Decimal
from typing import Dict, Any
from openai import OpenAI
from services.llm_service import LLMService

class TradingAgent:
    def __init__(self, openai_client: OpenAI):
        self.llm_service = LLMService(openai_client)

    def generate_trading_decision(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self._create_prompt(market_data)
            response = self.llm_service.generate_response(prompt)
            
            if "error" in response.get("content", "").lower():
                print(f"LLM Service Error: {response['content']}")
                return self._get_default_response(response["content"])
            
            return self._parse_response(response["content"])
            
        except Exception as e:
            print(f"Error in generate_trading_decision: {str(e)}")
            return self._get_default_response(str(e))

    def _parse_response(self, content: str) -> Dict[str, Any]:
        try:
            # Default values
            decision = {
                "action": "HOLD",
                "amount": Decimal("0.0"),
                "confidence": 0,
                "reasoning": content
            }
            
            # Parse the content for specific fields
            lines = content.split('\n')
            for line in lines:
                if line.startswith('Action:'):
                    decision['action'] = line.split(':')[1].strip()
                elif line.startswith('Amount:'):
                    try:
                        decision['amount'] = Decimal(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('Confidence:'):
                    try:
                        confidence = int(line.split(':')[1].strip().replace('%', ''))
                        decision['confidence'] = min(max(confidence, 0), 100)
                    except:
                        pass
                        
            return decision
            
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            return self._get_default_response(str(e))

    def _get_default_response(self, error_msg: str) -> Dict[str, Any]:
        return {
            "action": "HOLD",
            "amount": Decimal("0.0"),
            "confidence": 0,
            "reasoning": f"Error in analysis: {error_msg}"
        }

    def _create_prompt(self, market_data: Dict[str, Any]) -> str:
        return f"""
        Analyze the following market data and provide a trading decision:
        Current Price: ${market_data['price']:.2f}
        24h Change: {market_data['change_24h']:.2f}%
        Volume: {market_data['volume']:.2f}

        Based on this data, please provide:
        1. A trading action (BUY/SELL/HOLD)
        2. A position size (0-100)
        3. Your confidence level (0-100)
        4. Your reasoning

        Format your response exactly as follows:
        Action: [YOUR_DECISION]
        Amount: [YOUR_AMOUNT]
        Confidence: [YOUR_CONFIDENCE]
        Reasoning: [YOUR_DETAILED_ANALYSIS]
        """ 