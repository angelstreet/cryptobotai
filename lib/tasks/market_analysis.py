from typing import Dict, Any
from .base import Task

class MarketAnalysis(Task):
    def __init__(self, data_analyst):
        super().__init__("market_analysis")
        self.data_analyst = data_analyst
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute market analysis"""
        result = {}
        
        # Fetch historical and live data
        historical_data = self.data_analyst.fetch_historical_data(
            context['exchange'],
            context['symbol'],
            context.get('timeframe', '1h')
        )
        
        live_data = self.data_analyst.fetch_market_data(
            context['exchange'],
            context['symbol']
        )
        
        # Perform technical analysis
        technical_analysis = self.data_analyst.perform_technical_analysis(live_data)
        
        # Analyze sentiment
        sentiment = self.data_analyst.analyze_sentiment(context['symbol'])
        
        return {
            'historical_data': historical_data,
            'live_data': live_data,
            'technical_analysis': technical_analysis,
            'sentiment': sentiment
        } 