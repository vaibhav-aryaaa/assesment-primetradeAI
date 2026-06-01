import os

# Project root directory and data paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEAR_GREED_PATH = os.path.join(BASE_DIR, "fear_greed_index.csv")
HISTORICAL_DATA_PATH = os.path.join(BASE_DIR, "historical_data.csv")

# Output directory structure
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
PLOTS_DIR = os.path.join(OUTPUTS_DIR, "plots")

# Column name definitions for Fear & Greed dataset
FG_COL_DATE = "date"
FG_COL_VAL = "value"
FG_COL_CLASS = "classification"
FG_COL_TS = "timestamp"

# Column name definitions for Trader dataset
TRADER_COL_ACCOUNT = "Account"
TRADER_COL_COIN = "Coin"
TRADER_COL_EXEC_PRICE = "Execution Price"
TRADER_COL_SIZE_TOKENS = "Size Tokens"
TRADER_COL_SIZE_USD = "Size USD"
TRADER_COL_SIDE = "Side"
TRADER_COL_TS_IST = "Timestamp IST"
TRADER_COL_START_POS = "Start Position"
TRADER_COL_DIRECTION = "Direction"
TRADER_COL_CLOSED_PNL = "Closed PnL"
TRADER_COL_TX_HASH = "Transaction Hash"
TRADER_COL_ORDER_ID = "Order ID"
TRADER_COL_CROSSED = "Crossed"
TRADER_COL_FEE = "Fee"
TRADER_COL_TRADE_ID = "Trade ID"
TRADER_COL_TS = "Timestamp"
