import ccxt
import time
from src.config.trading_config import TRADING_CONFIG
from risk.risk_manager import RiskManager
from utils.indicators import calculate_indicators
from .position_tracker import PositionTracker

class MomentumTradingBot:
    def __init__(self, api_key, api_secret, logger):
        self.exchange = ccxt.kraken({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })
        self.logger = logger
        self.risk_manager = RiskManager()
        self.position_tracker = PositionTracker()
        self.config = TRADING_CONFIG

    def get_market_data(self):
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=self.config['trading_pair'],
                timeframe=self.config['timeframe'],
                limit=100
            )
            return calculate_indicators(ohlcv)
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None

    def generate_signal(self, data):
        if data is None:
            return None

        current_rsi = data['rsi'].iloc[-1]
        current_macd = data['macd'].iloc[-1]
        current_signal = data['signal'].iloc[-1]

        if (current_rsi < self.config['rsi_oversold'] and
                current_macd > current_signal):
            return 'buy'
        elif (current_rsi > self.config['rsi_overbought'] and
              current_macd < current_signal):
            return 'sell'
        return None

    def execute_trade(self, signal):
        try:
            balance = self.exchange.fetch_balance()
            usd_balance = balance['USD']['free']

            current_price = self.exchange.fetch_ticker(
                self.config['trading_pair']
            )['last']

            # Calculate position size
            trade_amount = self.risk_manager.calculate_position_size(
                balance=usd_balance,
                current_price=current_price
            )

            if signal == 'buy':
                order = self.exchange.create_market_buy_order(
                    self.config['trading_pair'],
                    trade_amount
                )
                self.position_tracker.add_position(
                    self.config['trading_pair'],
                    current_price,
                    trade_amount,
                    'long'
                )
                self.logger.info(f"Buy order executed: {order}")

            elif signal == 'sell':
                order = self.exchange.create_market_sell_order(
                    self.config['trading_pair'],
                    trade_amount
                )
                self.position_tracker.add_position(
                    self.config['trading_pair'],
                    current_price,
                    trade_amount,
                    'short'
                )
                self.logger.info(f"Sell order executed: {order}")

        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")

    def run(self):
        self.logger.info("Starting momentum trading bot...")

        while True:
            try:
                # Get market data and generate signal
                data = self.get_market_data()
                signal = self.generate_signal(data)

                if signal:
                    self.execute_trade(signal)

                # Check stop loss and take profit
                self.risk_manager.check_positions(
                    self.position_tracker.positions,
                    self.exchange
                )

                # Wait before next iteration
                time.sleep(60)

            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                time.sleep(60)
