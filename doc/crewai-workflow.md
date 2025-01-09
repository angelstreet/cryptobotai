# **AI Crypto Agency - Agents and Workflow**

This document outlines the **agents** and **workflow** for the AI Crypto Agency project. The system is designed to automate crypto trading using specialized AI agents, with a clear separation between **frontend** and **backend** components.

---

## **Agents List**

### **Frontend Agents**

#### **Receptionist Agent**
- **Role**: Interacts with the user.
- **Responsibilities**:
  - Displays a menu of options (e.g., live trade, portfolio update, backtest).
  - Forwards user requests to the **Orchestrator Agent**.
- **Key Features**:
  - User-friendly interface for task selection.
  - Handles user input and error messages.

---

### **Backend Agents**

#### **Orchestrator Agent**
- **Role**: Manages task routing and coordination.
- **Responsibilities**:
  - Adds tasks to a **task queue** for asynchronous processing.
  - Ensures tasks are executed in the correct order.
- **Key Features**:
  - Task prioritization and scheduling.
  - Handles communication between agents.

#### **LiveTraderAgent**
- **Role**: Executes live trades on the exchange.
- **Responsibilities**:
  - Runs continuously in the background using `asyncio`.
  - Fetches market data and makes trading decisions periodically.
- **Key Features**:
  - Non-blocking execution for real-time trading.
  - Handles trade execution and order monitoring.

#### **TestTraderAgent**
- **Role**: Simulates trades in a sandbox environment.
- **Responsibilities**:
  - Tests trading strategies without real money.
  - Provides feedback on strategy performance.
- **Key Features**:
  - Safe environment for testing and experimentation.
  - Simulates real-world trading conditions.

#### **BacktestTraderAgent**
- **Role**: Validates trading strategies using historical data.
- **Responsibilities**:
  - Runs backtests in a separate thread to avoid blocking the main thread.
  - Evaluates strategy performance and provides metrics.
- **Key Features**:
  - Handles CPU-intensive backtesting efficiently.
  - Generates detailed performance reports.

#### **PortfolioManagerAgent**
- **Role**: Manages the portfolio and evaluates performance.
- **Responsibilities**:
  - Provides portfolio updates on demand.
  - Evaluates risk exposure and adjusts strategies.
- **Key Features**:
  - Real-time portfolio tracking.
  - Risk analysis and performance evaluation.

#### **DataAnalystAgent**
- **Role**: Fetches and analyzes market data.
- **Responsibilities**:
  - Provides historical and live market data to other agents.
  - Performs technical and sentiment analysis.
- **Key Features**:
  - Supports data-driven decision-making.
  - Handles data fetching and preprocessing.

---

## **Workflow Summary**

### **1. User Interaction**
- The **Receptionist Agent (frontend)** interacts with the user and displays available tasks (e.g., live trade, portfolio update, backtest).
- The user selects a task, and the Receptionist forwards the request to the **Orchestrator Agent (backend)**.

### **2. Task Routing**
- The **Orchestrator Agent (backend)** adds the task to a **task queue** for asynchronous processing.
- Tasks are processed by the appropriate agent (e.g., LiveTraderAgent, BacktestTraderAgent, PortfolioManagerAgent).

### **3. Continuous Tasks**
- The **LiveTraderAgent (backend)** runs continuously in the background using `asyncio`.
- It periodically fetches market data, makes trading decisions, and executes trades.

### **4. On-Demand Tasks**
- Tasks like portfolio updates or backtests are added to the **task queue** by the Orchestrator.
- Workers process these tasks asynchronously without blocking the main thread.

### **5. CPU-Intensive Tasks**
- Tasks like backtesting are executed in a separate thread using **threading** or **multiprocessing** to avoid blocking the main thread.

### **6. Event-Driven Updates**
- An **Event Manager** triggers tasks based on events (e.g., market data updates, user requests).
- For example, a market data update event triggers the LiveTraderAgent.

---

## **Key Systems**

### **1. Async**
- Used for non-blocking execution of continuous and on-demand tasks.
- Ensures that the system remains responsive during live trading.

### **2. Queue**
- Manages on-demand tasks efficiently.
- Tasks are added to the queue by the Orchestrator and processed asynchronously.

### **3. Threading**
- Handles CPU-intensive tasks like backtesting in a separate thread.
- Prevents blocking of the main thread during resource-heavy operations.

---

This README provides a clear overview of the **agents**, **workflow**, and **key systems** in your AI Crypto Agency project. You can use this as a reference for developers and stakeholders. 🚀