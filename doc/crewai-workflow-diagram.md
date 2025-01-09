1. High-Level Workflow Diagram
[User]
   |
   v
[Receptionist Agent (Frontend)]
   |
   v
[Orchestrator Agent (Backend)]
   |
   +--> [Task Queue]
   |        |
   |        v
   |    [Workers] --> [Backend Agents]
   |
   v
[Event Manager]
   |
   +--> [LiveTraderAgent (Continuous)]
   +--> [BacktestTraderAgent (Threaded)]
   +--> [PortfolioManagerAgent (On-Demand)]

2. Agent Interaction Diagram
[User]
   |
   v
[Receptionist Agent (Frontend)]
   |
   v
[Orchestrator Agent (Backend)]
   |
   +--> [LiveTraderAgent] (Runs continuously using asyncio)
   +--> [TestTraderAgent] (Sandbox trading)
   +--> [BacktestTraderAgent] (Runs in a separate thread)
   +--> [PortfolioManagerAgent] (On-demand portfolio updates)
   +--> [DataAnalystAgent] (Fetches and analyzes market data)

3. Task Flow Diagram
[User Request] --> [Receptionist Agent]
                       |
                       v
                  [Orchestrator Agent]
                       |
                       v
                  [Task Queue]
                       |
                       +--> [LiveTraderAgent] (Continuous)
                       +--> [BacktestTraderAgent] (Threaded)
                       +--> [PortfolioManagerAgent] (On-Demand)
4. Event-Driven Updates Diagram
[Market Data Update] --> [Event Manager]
                             |
                             v
                        [LiveTraderAgent] (Executes trades)
                             |
                             v
                        [PortfolioManagerAgent] (Updates portfolio)

[User Request] --> [Event Manager]
                       |
                       v
                  [BacktestTraderAgent] (Runs backtest)
                       |
                       v
                  [PortfolioManagerAgent] (Evaluates performance)
5. Key Systems Diagram
[Async] --> [LiveTraderAgent] (Non-blocking continuous execution)
[Queue] --> [Task Queue] (Manages on-demand tasks)
[Threading] --> [BacktestTraderAgent] (Handles CPU-intensive tasks)