from src.config.trading_config import TRADING_CONFIG  # Updated import
from src.backtest.backtest import MomentumBacktest  # Updated import
import matplotlib.pyplot as plt

def plot_results(results_df, trades_df):
    plt.figure(figsize=(15, 10))

    # Plot balance over time
    plt.subplot(2, 1, 1)
    plt.plot(results_df['timestamp'], results_df['balance'])
    plt.title('Account Balance Over Time')
    plt.xlabel('Date')
    plt.ylabel('Balance')

    # Plot price with buy/sell signals
    plt.subplot(2, 1, 2)
    plt.plot(results_df['timestamp'], results_df['close'])

    # Plot buy signals
    buys = trades_df[trades_df['type'] == 'buy']
    plt.scatter(buys['timestamp'], buys['price'],
                marker='^', color='g', label='Buy')

    # Plot sell signals
    sells = trades_df[trades_df['type'] == 'sell']
    plt.scatter(sells['timestamp'], sells['price'],
                marker='v', color='r', label='Sell')

    plt.title('Price with Trading Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    plt.tight_layout()
    plt.show()

def main():
    # Initialize backtest
    backtest = MomentumBacktest(TRADING_CONFIG)

    # Run backtest
    results = backtest.run_backtest()

    if results is None:
        print("Backtest failed to run")
        return

    # Print metrics
    print("\nBacktest Results:")
    print("=" * 40)
    for metric, value in results['metrics'].items():
        print(f"{metric}: {value:.2f}")

    # Plot results
    plot_results(results['results'], results['trades'])

    # Save detailed results to CSV
    results['results'].to_csv('backtest_results.csv', index=False)
    results['trades'].to_csv('backtest_trades.csv', index=False)

if __name__ == "__main__":
    main()
