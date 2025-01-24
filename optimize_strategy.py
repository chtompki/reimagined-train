from src.config.trading_config import TRADING_CONFIG
from src.backtest.optimizer import StrategyOptimizer

def main():
    optimizer = StrategyOptimizer(TRADING_CONFIG)
    results_df, best_params = optimizer.optimize_parameters()

    print("\nOptimization Results:")
    print("=" * 40)
    print("\nBest Parameters:")
    for param, value in best_params.items():
        print(f"{param}: {value}")

    # Save results
    results_df.to_csv('optimization_results.csv', index=False)

if __name__ == "__main__":
    main()
