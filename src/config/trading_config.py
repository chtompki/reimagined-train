# Trading parameters
TRADING_CONFIG = {
    'exchange_id': 'kraken',
    'trading_pair': 'BTC/USD',
    'timeframe': '1h',

    # Updated parameters
    'position_size': 0.02,  # Increased from 0.01
    'rsi_period': 10,      # Changed from 14
    'rsi_overbought': 75,  # Changed from 70
    'rsi_oversold': 25,    # Changed from 30
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    # New parameters
    'volume_threshold': 1.2,
    'trailing_stop_pct': 0.02,
    'volatility_threshold': 2.5,
}
