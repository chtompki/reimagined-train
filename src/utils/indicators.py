import pandas as pd
from src.config.trading_config import TRADING_CONFIG

def calculate_indicators(ohlcv_data):
    df = pd.DataFrame(
        ohlcv_data,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(
        window=TRADING_CONFIG['rsi_period']
    ).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(
        window=TRADING_CONFIG['rsi_period']
    ).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Calculate MACD
    exp1 = df['close'].ewm(
        span=TRADING_CONFIG['macd_fast'],
        adjust=False
    ).mean()
    exp2 = df['close'].ewm(
        span=TRADING_CONFIG['macd_slow'],
        adjust=False
    ).mean()
    df['macd'] = exp1 - exp2
    df['signal'] = df['macd'].ewm(
        span=TRADING_CONFIG['macd_signal'],
        adjust=False
    ).mean()

    # Add volume indicators
    df['volume_sma'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma']

    return df
