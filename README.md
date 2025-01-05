# CryptobotAI: AI-Powered Cryptocurrency Trading Bot  

A sophisticated cryptocurrency trading bot that leverages **OpenAI's Claude-3 model** for market analysis and automated trading decisions. This project is forked from [Virattt's AI Hedge Fund](https://github.com/virattt/ai-hedge-fund) and customized to focus on cryptocurrency markets.  

---

## **Features**  

### **Core Features**  
- 🤖 **AI-Powered Trading Decisions**: Utilizes Claude-3 for real-time market analysis and decision-making.  
- 📊 **Real-Time Market Data**: Fetches data via CCXT for accurate and up-to-date market insights.  
- 🔄 **Advanced Backtesting Engine**: Test strategies on historical data before deploying them live.  
- 📈 **Performance Tracking**: Detailed analytics and trade logging for performance evaluation.  
- 💼 **Multi-Exchange Support**: Integrates with popular exchanges like Binance, Coinbase Pro, and more.  
- ⚙️ **Configurable Trading Parameters**: Customize strategies, risk management, and trading parameters.  

### **Trading Features**  
- Real-time market analysis.  
- Dynamic position sizing.  
- Risk management controls.  
- Trading fee consideration.  
- Multiple timeframe support.  

### **Backtesting Features**  
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
   Rename `.env.example` to `.env` and add your API keys:  
   ```env
   OPENROUTER_API_KEY=your_api_key_here
   APP_URL=http://localhost:3000
   APP_NAME=Crypto AI Trading Bot
   ```  

3. **Run the Bot**:  

   **Live Trading**:  
   ```bash
   python main.py --symbol BTC/USDT --show-reasoning
   ```  

   **Backtesting with Date Range**:  
   ```bash
   python main.py --symbol BTC/USDT --backtest --start-date 01/12/2024 --end-date 30/12/2024 --initial-balance 10000
   ```  

   **Backtesting with Number of Days**:  
   ```bash
   python main.py --symbol BTC/USDT --backtest --backtest-days 30 --initial-balance 10000
   ```  

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