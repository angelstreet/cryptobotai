from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime

class TradingVisualizer:
    def __init__(self, market_data: pd.DataFrame, trades: List[Dict]):
        self.market_data = market_data
        self.trades = trades
        self.console = Console()

    def plot_ascii_candlesticks(self, width: int = 80, height: int = 24):
        """Draw candlestick chart using ASCII/Unicode characters"""
        # Calculate time range
        start_date = self.market_data['timestamp'].iloc[0]
        end_date = self.market_data['timestamp'].iloc[-1]
        days_diff = (end_date - start_date).days
        
        # Determine time range indicator
        if days_diff <= 1:
            time_range = "24H"
        elif days_diff <= 7:
            time_range = "7D"
        elif days_diff <= 30:
            time_range = "30D"
        else:
            time_range = f"{days_diff}D"
        
        self.console.print(f"\n=== Market Analysis ({time_range}) ===\n")
        
        df = self.market_data.copy()
        
        # Calculate price metrics
        min_price = df[['low']].min().min()
        max_price = df[['high']].max().max()
        price_range = max_price - min_price
        
        # Normalize prices to fit height
        def normalize(price):
            return int((price - min_price) / price_range * (height - 1))
        
        # Create candlesticks
        chart_lines = [[] for _ in range(height)]
        
        # Calculate visible candles based on width
        step = max(1, len(df) // (width - 10))
        visible_df = df.iloc[::step]
        
        # Draw candlesticks
        for idx, row in visible_df.iterrows():
            open_norm = normalize(row['open'])
            close_norm = normalize(row['close'])
            high_norm = normalize(row['high'])
            low_norm = normalize(row['low'])
            
            is_bullish = row['close'] >= row['open']
            color = 'green' if is_bullish else 'red'
            body_char = '█'
            
            # Draw the candle
            for y in range(height):
                if y == high_norm:
                    chart_lines[height-1-y].append(f'[{color}]╽[/]')
                elif y == low_norm:
                    chart_lines[height-1-y].append(f'[{color}]╿[/]')
                elif min(open_norm, close_norm) <= y <= max(open_norm, close_norm):
                    chart_lines[height-1-y].append(f'[{color}]{body_char}[/]')
                elif low_norm < y < high_norm:
                    chart_lines[height-1-y].append(f'[{color}]│[/]')
                else:
                    chart_lines[height-1-y].append(' ')
        
        # Add price labels
        price_labels = []
        for i in range(height):
            price = max_price - (i * price_range / (height - 1))
            label = f'${price:,.2f}'
            price_labels.append(label.rjust(10))
        
        # Combine price labels and chart
        for i in range(height):
            chart_lines[i] = price_labels[i] + ' ' + ''.join(chart_lines[i])
        
        # Create date labels
        date_labels = []
        label_positions = np.linspace(0, len(visible_df) - 1, 5).astype(int)
        for pos in label_positions:
            date = visible_df.index[pos] if isinstance(visible_df.index[pos], pd.Timestamp) else pd.Timestamp(visible_df['timestamp'].iloc[pos])
            date_labels.append(date.strftime('%Y-%m-%d %H:%M'))
        
        # Create and print the visualization
        chart_text = '\n'.join(chart_lines)
        start_date = df['timestamp'].iloc[0].strftime('%Y-%m-%d %H:%M')
        end_date = df['timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M')
        
        panel = Panel(
            Text.from_markup(chart_text),
            title=f"[bold blue]Candlestick Chart[/] ({start_date} to {end_date})",
            subtitle=f"Range: ${min_price:,.2f} - ${max_price:,.2f}",
            border_style="blue",
            box=box.ROUNDED
        )
        self.console.print(panel)
        
        # Print date labels
        date_text = ' '.join(f'{d:^16}' for d in date_labels)
        self.console.print(f"\n{' ' * 10}{date_text}")

    def print_trade_summary(self):
        """Print a rich table with trade summary"""
        if not self.trades:
            self.console.print("\n[yellow]No trades to display[/]")
            return
            
        table = Table(
            title="Trade History",
            box=box.ROUNDED,
            border_style="blue",
            header_style="bold blue"
        )
        
        table.add_column("Date", justify="center")
        table.add_column("Action", justify="center")
        table.add_column("Price", justify="right")
        table.add_column("Amount", justify="right")
        table.add_column("Value", justify="right")
        
        for trade in self.trades:
            action_color = "green" if trade['action'] == 'BUY' else "red"
            value = trade['price'] * trade['amount']
            marker = "▲" if trade['action'] == 'BUY' else "▼"
            
            table.add_row(
                trade['timestamp'].strftime('%Y-%m-%d %H:%M'),
                f"[{action_color}]{marker} {trade['action']}[/]",
                f"${trade['price']:,.2f}",
                f"{trade['amount']:.6f}",
                f"${value:,.2f}"
            )
        
        self.console.print("\n")
        self.console.print(table)

    def plot_chart(self):
        """Display complete trading visualization"""
        self.print_trade_summary()
        self.plot_ascii_candlesticks() 