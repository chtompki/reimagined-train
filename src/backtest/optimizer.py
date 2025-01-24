from src.backtest.backtest import MomentumBacktest
import itertools
import pandas as pd

class StrategyOptimizer:
    def __init__(self, base_config):
        self.base_config = base_config

    def optimize_parameters(self):
        parameter_ranges = {
            'rsi_period': range(10, 21, 2),
            'rsi_overbought': range(65, 81, 5),
            'rsi_oversold': range(20, 36, 5),
            'position_size': [0.01, 0.02, 0.03],
            'volume_threshold': [1.1, 1.2, 1.3]
        }

        results = []
        best_return = -float('inf')
        best_params = {}

        # Generate all combinations
        keys = parameter_ranges.keys()
        combinations = itertools.product(*parameter_ranges.values())

        for combo in combinations:
            config = self.base_config.copy()
            for key, value in zip(keys, combo):
                config[key] = value

            backtest = MomentumBacktest(config)
            result = backtest.run_backtest()

            if result['metrics']['Total Return (%)'] > best_return:
                best_return = result['metrics']['Total Return (%)']
                best_params = {k: v for k, v in zip(keys, combo)}

            results.append({
                'parameters': {k: v for k, v in zip(keys, combo)},
                'metrics': result['metrics']
            })

        return pd.DataFrame(results), best_params
