import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..utils.indicators import calculate_indicators
from .performance_metrics import calculate_performance_metrics

class MomentumBacktest:
    def __init__(self, config, initial_balance=10000):
        self.exchange = ccxt.kraken()
        self.config = config
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = []
        self.trades = []

    def adjust_for_volatility(self, volatility):
        if volatility > self.config['volatility_threshold']:
            self.config['position_size'] = self.original_position_size * 0.8
            self.config['rsi_period'] = 10
        else:
            self.config['position_size'] = self.original_position_size
            self.config['rsi_period'] = 14

    def update_stop_loss(self, current_price):
        for position in self.positions:
            if position['type'] == 'long':
                new_stop = current_price * (1 - self.config['trailing_stop_pct'])
                position['stop_loss'] = max(position.get('stop_loss', 0), new_stop)

    def generate_signal(self, row):
        # Volume confirmation
        volume_confirmed = row['volume_ratio'] > self.config['volume_threshold']

        if (row['rsi'] < self.config['rsi_oversold'] and
                row['macd'] > row['signal'] and
                volume_confirmed):
            return 'buy'
        elif (row['rsi'] > self.config['rsi_overbought'] and
              row['macd'] < row['signal'] and
              volume_confirmed):
            return 'sell'
        return None

    def fetch_historical_data(self, days=30):
        try:
            # Calculate timestamp for 30 days ago
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=self.config['trading_pair'],
                timeframe=self.config['timeframe'],
                since=int(start_time.timestamp() * 1000),
                limit=None  # Fetch all available data points
            )

            # Convert to DataFrame and calculate indicators
            df = calculate_indicators(ohlcv)
            return df

        except Exception as e:
            print(f"Error fetching historical data: {str(e)}")
            return None

    def execute_trade(self, signal, price, timestamp):
        position_size = self.balance * self.config['position_size']

        if signal == 'buy':
            # Calculate number of coins we can buy
            coins = position_size / price
            cost = coins * price

            if cost <= self.balance:
                self.balance -= cost
                self.positions.append({
                    'type': 'long',
                    'entry_price': price,
                    'coins': coins,
                    'timestamp': timestamp
                })
                self.trades.append({
                    'timestamp': timestamp,
                    'type': 'buy',
                    'price': price,
                    'amount': coins,
                    'cost': cost,
                    'balance': self.balance
                })

        elif signal == 'sell':
            # Check if we have an open position to close
            if self.positions:
                position = self.positions[-1]
                if position['type'] == 'long':
                    sale_value = position['coins'] * price
                    self.balance += sale_value
                    profit = sale_value - (position['coins'] * position['entry_price'])

                    self.trades.append({
                        'timestamp': timestamp,
                        'type': 'sell',
                        'price': price,
                        'amount': position['coins'],
                        'profit': profit,
                        'balance': self.balance
                    })
                    self.positions.pop()

    def run_backtest(self):
        # Fetch historical data
        data = self.fetch_historical_data()
        if data is None:
            return None

        # Initialize results storage
        results = []
        self.balance = self.initial_balance
        self.positions = []
        self.trades = []

        # Iterate through each candle
        for index, row in data.iterrows():
            # Generate trading signal
            signal = self.generate_signal(row)

            # Execute trade if signal exists
            if signal:
                self.execute_trade(signal, row['close'], row['timestamp'])

            # Store daily results
            results.append({
                'timestamp': row['timestamp'],
                'close': row['close'],
                'balance': self.balance,
                'signal': signal
            })

        # Calculate performance metrics
        results_df = pd.DataFrame(results)
        trades_df = pd.DataFrame(self.trades)

        metrics = calculate_performance_metrics(
            results_df,
            trades_df,
            self.initial_balance
        )

        # Add volatility calculation
        returns = data['close'].pct_change()
        volatility = returns.std() * np.sqrt(252)
        self.adjust_for_volatility(volatility)

        # In the main loop
        for index, row in data.iterrows():
            # Update trailing stops
            if self.positions:
                self.update_stop_loss(row['close'])

        return {
            'results': results_df,
            'trades': trades_df,
            'metrics': metrics
        }
