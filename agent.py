from decimal import Decimal
from typing import Dict, Any
from openai import OpenAI

class TradingAgent:
    def __init__(self, openai_client: OpenAI, 
                 max_position_size: Decimal = Decimal('1000'),
                 stop_loss_pct: Decimal = Decimal('0.02')):
        self.client = openai_client
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct

    def generate_trading_decision(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self._generate_llm_response(self._create_prompt(market_data))
            return self._parse_response(response)
        except Exception as e:
            print(f"Error in generate_trading_decision: {str(e)}")
            return self._get_default_response(str(e))

    def _generate_llm_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[
                    {"role": "system", "content": "You are a trading assistant that analyzes market data and provides trading decisions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def _parse_response(self, content: str) -> Dict[str, Any]:
        decision = {
            "action": "HOLD",
            "amount": Decimal("0.0"),
            "confidence": 0,
            "reasoning": content
        }
        
        try:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('Action:'):
                    decision['action'] = line.split(':')[1].strip()
                elif line.startswith('Amount:'):
                    decision['amount'] = min(
                        Decimal(line.split(':')[1].strip()),
                        self.max_position_size
                    )
                elif line.startswith('Confidence:'):
                    confidence = int(line.split(':')[1].strip().replace('%', ''))
                    decision['confidence'] = min(max(confidence, 0), 100)
            
            return decision
        except Exception as e:
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