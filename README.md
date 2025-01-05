# Crypto AI Trading Bot

## TODO Features

### 1. Multi-Pair Trading Support
- [ ] Add configuration files for different crypto pair lists:
  - top10.json
  - top25.json
  - top50.json
  - top100.json
  - default.json (BTC/USDT only)
- [ ] Implement market scanner to analyze multiple pairs
- [ ] Add parallel processing for faster multi-pair analysis
- [ ] Add priority/weighting system for pair selection
- [ ] Implement risk management across multiple pairs

### 2. Automated Config Optimization
- [ ] Add backtesting optimization module
- [ ] Support testing multiple configurations:
  - Different threshold combinations
  - Various volatility multipliers
  - Position sizing strategies
- [ ] Implement performance metrics:
  - Sharpe ratio
  - Maximum drawdown
  - Win rate
  - Risk-adjusted returns
- [ ] Add configuration generation based on market conditions
- [ ] Create optimization reports with best configurations
- [ ] Support quiet/mute mode for batch testing

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# AI Provider Configuration
AI_API_KEY=your_api_key_here
AI_MODEL=mistralai/mistral-7b-instruct
AI_API_URL=https://openrouter.ai/api/v1
AI_PROVIDER=openrouter  # Options: openrouter, openai, anthropic, etc.

# Application Settings
APP_URL=http://localhost:3000
APP_NAME=Crypto AI Trading Bot
```

### Provider Examples

#### OpenRouter
```env
AI_PROVIDER=openrouter
AI_API_URL=https://openrouter.ai/api/v1
AI_MODEL=mistralai/mistral-7b-instruct
```

#### OpenAI
```env
AI_PROVIDER=openai
AI_API_URL=https://api.openai.com/v1
AI_MODEL=gpt-4-turbo-preview
```

#### Anthropic
```env
AI_PROVIDER=anthropic
AI_API_URL=https://api.anthropic.com/v1
AI_MODEL=claude-3-sonnet
```