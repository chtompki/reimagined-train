from dotenv import load_dotenv
import os
from bot.momentum_bot import MomentumTradingBot
from utils.logger import setup_logger

def main():
    # Load environment variables
    load_dotenv()

    # Setup logger
    logger = setup_logger()

    # Initialize bot
    bot = MomentumTradingBot(
        api_key=os.getenv('KRAKEN_API_KEY'),
        api_secret=os.getenv('KRAKEN_SECRET'),
        logger=logger
    )

    # Run bot
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {str(e)}")

if __name__ == "__main__":
    main()
