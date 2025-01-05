# Crypto AI Trading Bot

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