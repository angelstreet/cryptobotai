# Crypto Trading Bot with AI Agents

This project implements a crypto trading bot using AI agents with the `crewai` framework. The bot is designed to automate trading decisions by analyzing market data, developing strategies, backtesting them, and executing trades on an exchange.

---

## **Overview**

The bot consists of four specialized AI agents, each responsible for a specific part of the trading workflow:

1. **Data Analyst**: Fetches and analyzes market data (historical and live).
2. **Portfolio Manager**: Develops trading strategies, manages the portfolio, and evaluates risk exposure.
3. **Backtester**: Validates strategies using historical data.
4. **Trader**: Executes live trades on the exchange.

The workflow follows a logical sequence: **Data → Analysis → Strategy → Backtesting → Execution → Evaluation**.

---

## **Agent Roles and Responsibilities**

### **1. Data Analyst**
- **Role**: Fetch and analyze market data.
- **Tasks**:
  - Fetch historical and live market data.
  - Perform technical, fundamental, and sentiment analysis.
  - Periodically refresh live data for real-time insights.
- **Tools**:
  - `fetch_historical_data`
  - `fetch_live_data`
  - `technical_analysis`
  - `sentiment_analysis`

### **2. Portfolio Manager**
- **Role**: Develop strategies, manage the portfolio, and evaluate risk exposure.
- **Tasks**:
  - Develop and optimize trading strategies.
  - Manage portfolio allocation (Buy/Hold/Sell decisions).
  - Evaluate risk exposure and adjust strategies accordingly.
  - Regularly evaluate portfolio performance (post-trade analysis).
- **Tools**:
  - `strategy_development`
  - `portfolio_management`
  - `risk_analysis`
  - `performance_evaluation`

### **3. Backtester**
- **Role**: Test strategies on historical data.
- **Tasks**:
  - Backtest strategies using historical data.
  - Provide performance metrics and insights to the Portfolio Manager.
- **Tools**:
  - `backtest_strategy`
  - `historical_data_analysis`

### **4. Trader**
- **Role**: Execute live trades on the exchange.
- **Tasks**:
  - Execute trading orders (Buy/Sell) as directed by the Portfolio Manager.
  - Monitor order execution and minimize slippage.
- **Tools**:
  - `execute_trade`
  - `order_monitoring`

---

## **Workflow**

1. **Data Analysis**:
   - The **Data Analyst** fetches historical and live market data and performs analysis (technical, fundamental, sentiment).

2. **Strategy Development**:
   - The **Portfolio Manager** uses insights from the Data Analyst to develop and optimize trading strategies.

3. **Backtesting**:
   - The **Backtester** validates strategies using historical data and provides performance metrics to the Portfolio Manager.

4. **Trade Execution**:
   - The **Trader** executes live trades on the exchange as directed by the Portfolio Manager.

5. **Performance Evaluation**:
   - The **Portfolio Manager** evaluates post-trade performance and adjusts strategies as needed.

---

## **Task Repartition**

| Task                                | Responsible Agent       |
|-------------------------------------|-------------------------|
| Fetch historical and live data      | Data Analyst            |
| Perform technical analysis          | Data Analyst            |
| Perform sentiment analysis          | Data Analyst            |
| Develop trading strategies          | Portfolio Manager       |
| Backtest strategies                 | Backtester              |
| Manage portfolio allocation         | Portfolio Manager       |
| Evaluate risk exposure              | Portfolio Manager       |
| Execute live trades                 | Trader                  |
| Monitor trade execution             | Trader                  |
| Evaluate post-trade performance     | Portfolio Manager       |
| Regularly review portfolio          | Portfolio Manager       |