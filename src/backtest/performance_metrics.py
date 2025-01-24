import numpy as np
import pandas as pd

def calculate_performance_metrics(results_df, trades_df, initial_balance):
    """Calculate various performance metrics from backtest results"""

    # Calculate returns
    final_balance = results_df['balance'].iloc[-1]
    total_return = (final_balance - initial_balance) / initial_balance * 100

    # Calculate daily returns
    daily_returns = results_df['balance'].pct_change().dropna()

    # Calculate metrics
    metrics = {
        'Initial Balance': initial_balance,
        'Final Balance': final_balance,
        'Total Return (%)': total_return,
        'Number of Trades': len(trades_df),
        'Win Rate (%)': calculate_win_rate(trades_df) if not trades_df.empty else 0,
        'Average Profit per Trade': calculate_avg_profit(trades_df) if not trades_df.empty else 0,
        'Max Drawdown (%)': calculate_max_drawdown(results_df['balance']),
        'Sharpe Ratio': calculate_sharpe_ratio(daily_returns),
        'Volatility (%)': daily_returns.std() * np.sqrt(365) * 100
    }

    return metrics

def calculate_win_rate(trades_df):
    if 'profit' not in trades_df.columns:
        return 0
    winning_trades = len(trades_df[trades_df['profit'] > 0])
    total_trades = len(trades_df)
    return (winning_trades / total_trades * 100) if total_trades > 0 else 0

def calculate_avg_profit(trades_df):
    if 'profit' not in trades_df.columns:
        return 0
    return trades_df['profit'].mean()

def calculate_max_drawdown(balance_series):
    rolling_max = balance_series.expanding().max()
    drawdowns = (balance_series - rolling_max) / rolling_max * 100
    return abs(drawdowns.min())

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    excess_returns = returns - risk_free_rate/365
    return np.sqrt(365) * (excess_returns.mean() / excess_returns.std())
