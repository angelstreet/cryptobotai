# CryptobotAI: AI-Powered Cryptocurrency Trading Bot  

A sophisticated cryptocurrency trading bot that leverages multiple AI providers for market analysis and automated trading decisions:
- 🤖 **OpenAI**: GPT-3.5/4 models
- 🧠 **Claude**: Anthropic's Claude models
- 🌐 **OpenRouter**: Access to various open-source models
- 💻 **Local LLMs**: Run models locally using Ollama

## Features  

### Core Features  
- 🤖 **Multiple AI Provider Support**: 
  - OpenAI GPT models
  - Anthropic Claude
  - OpenRouter models
  - Local models via Ollama
- 📊 **Real-Time Market Data**: Fetches data via CCXT
- 🔄 **Advanced Backtesting Engine**
- 📈 **Performance Tracking**
- 💼 **Multi-Exchange Support**
- ⚙️ **Configurable Trading Parameters**

### Trading Features  
- Real-time market analysis.  
- Dynamic position sizing.  
- Risk management controls.  
- Trading fee consideration.  
- Multiple timeframe support.  

### Backtesting Features  
- **Flexible Date Range**: Backtest over a specific date range or a number of days.  
- **Historical Data Fetching**: Automatically fetches and filters historical data for the specified period.  
- **Pagination Handling**: Supports longer time ranges by handling pagination seamlessly.  
- **Detailed Results**: Includes the exact date range in the output for clarity.  

---

## **Quick Start**  

1. **Clone and Install**:  
   ```bash
   git clone https://github.com/angelstreet/cryptobotai.git
   cd cryptobotai
   pip install -r requirements.txt
   ```  

2. **Configure `.env`**:  
   Rename `.env.example` to `.env` and configure your preferred AI provider:

   **For OpenAI**:
   ```env
   AI_PROVIDER=OPENAI
   OPENAI_API_KEY=your_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

   **For Local LLM (Ollama)**:
   ```env
   AI_PROVIDER=LOCAL
   LOCAL_API_URL=http://localhost:11434
   LOCAL_MODEL=llama2
   ```

3. **For Local LLM Setup**:
   ```bash
   # Install Ollama
   curl https://ollama.ai/install.sh | sh
   
   # Pull your preferred model
   ollama pull llama2  # or mistral, codellama, etc.
   
   # Start Ollama
   ollama serve
   ```

4. **Run the Bot**:  
   ```bash
   python main.py --symbol BTC/USDT --show-reasoning
   ```

## AI Provider Configuration

### OpenAI
- Requires API key
- Supports GPT-3.5 and GPT-4 models
- Best for high-accuracy trading decisions

### Claude
- Requires Anthropic API key
- Supports Claude-3 models
- Excellent for detailed market analysis

### OpenRouter
- Access to various open-source models
- Requires OpenRouter API key
- Good for testing different models

### Local LLM (Ollama)
- No API key required
- Run models locally
- Supported models:
  - llama2
  - mistral
  - codellama
  - neural-chat
  - and more
- Great for testing and development
- Lower latency, no API costs

---

## **Command Line Options**  

| Option | Description | Default | Example |  
|--------|-------------|---------|---------|  
| `--symbol` | Trading pair | Required | `BTC/USDT` |  
| `--exchange` | Exchange to use | binance | `coinbase` |  
| `--timeframe` | Trading interval | 1h | `15m`, `4h`, `1d` |  
| `--show-reasoning` | Show AI analysis | False | - |  
| `--backtest` | Run in backtest mode | False | - |  
| `--backtest-days` | Backtest duration in days | 30 | `7`, `90` |  
| `--start-date` | Start date for backtest (DD/MM/YYYY) | - | `01/12/2024` |  
| `--end-date` | End date for backtest (DD/MM/YYYY) | - | `30/12/2024` |  
| `--initial-balance` | Starting balance | 10000 | `5000` |  

---

## **Example Commands**  

### **Basic Live Trading**  
```bash
python main.py --symbol BTC/USDT
```  

### **Live Trading with Analysis**  
```bash
python main.py --symbol BTC/USDT --show-reasoning --timeframe 15m
```  

### **Backtest with Date Range**  
```bash
python main.py --symbol BTC/USDT --backtest --start-date 01/12/2024 --end-date 30/12/2024 --initial-balance 10000
```  

### **Backtest with Number of Days**  
```bash
python main.py --symbol BTC/USDT --backtest --backtest-days 30 --initial-balance 10000
```  

### **Custom Exchange**  
```bash
python main.py --symbol BTC/USDT --exchange coinbase --timeframe 4h
```  

---

## **Output Examples**  

### **Backtest Summary**  
```
Starting backtest simulation...
Date Range: 01/12/2024 - 30/12/2024
Initial Balance: $10000.00
==================================================
Final Balance: $12450.32
Final Position: 0.15000000
Final Portfolio Value: $15780.45
Total Return: 57.80%
Maximum Drawdown: 12.35%
Number of Trades: 24
```  

### **Trade Details**  
```
Date: 2024-03-15 14:00
Action: BUY
Price: $45678.90
Amount: 0.150000
Fee: $6.85
Reasoning: Strong upward momentum with increasing volume...
```  

---

## **Project Structure**  
```
cryptobotai/
├── main.py          # Entry point and CLI
├── agent.py         # Trading agent with LLM integration
├── backtester.py    # Backtesting engine
├── requirements.txt # Dependencies
└── .env            # Configuration
```  

---

## **Dependencies**  
```
openai         # AI model integration
python-dotenv  # Configuration
ccxt          # Exchange API
pandas        # Data handling
```  

---

## **Forked Repository**  
This project is forked from [Virattt's AI Hedge Fund](https://github.com/virattt/ai-hedge-fund). Special thanks to [Virattt](https://github.com/virattt) for the original work, which served as the foundation for this cryptocurrency-focused adaptation.  

---

## **Disclaimer**  
⚠️ **This is an educational project.** Cryptocurrency trading involves significant risk. Never trade with funds you cannot afford to lose. The bot's performance is not guaranteed.  

---

## **License**  
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  

---

## **Contributing**  
Contributions are welcome! If you'd like to contribute, please:  
1. Fork the repository.  
2. Create a new branch for your feature or bugfix.  
3. Submit a pull request with a detailed description of your changes.  

---

## **Support**  
- 📖 [Documentation](https://github.com/angelstreet/cryptobotai/wiki)  
- 🐛 [Issue Tracker](https://github.com/angelstreet/cryptobotai/issues)  
- 💬 [Discussions](https://github.com/angelstreet/cryptobotai/discussions)  

---

Built with ❤️ by [angelstreet](https://github.com/angelstreet).  

Happy trading! 🚀