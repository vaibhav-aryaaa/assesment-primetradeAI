import pandas as pd
import numpy as np
import logging
from src import config

# Set up simple logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_fear_greed_data(file_path=config.FEAR_GREED_PATH):
    """
    Loads and cleans the Bitcoin Fear and Greed Index dataset.
    """
    logger.info(f"Loading Fear & Greed dataset from {file_path}")
    try:
        df = pd.read_csv(file_path)
        
        # Convert date to datetime
        df[config.FG_COL_DATE] = pd.to_datetime(df[config.FG_COL_DATE])
        
        # Convert value to numeric
        df[config.FG_COL_VAL] = pd.to_numeric(df[config.FG_COL_VAL], errors='coerce')
        
        # Drop rows with critical missing columns
        df = df.dropna(subset=[config.FG_COL_DATE, config.FG_COL_VAL])
        
        # Sort by date
        df = df.sort_values(by=config.FG_COL_DATE).reset_index(drop=True)
        
        logger.info(f"Successfully loaded Fear & Greed: {df.shape[0]} rows, date range {df[config.FG_COL_DATE].min().date()} to {df[config.FG_COL_DATE].max().date()}")
        return df
    except Exception as e:
        logger.error(f"Error loading Fear & Greed dataset: {e}")
        raise

def load_trader_data(file_path=config.HISTORICAL_DATA_PATH):
    """
    Loads and cleans the Historical Trader Data from Hyperliquid.
    """
    logger.info(f"Loading Trader dataset from {file_path}")
    try:
        # Load data
        df = pd.read_csv(file_path)
        
        # Convert numeric columns
        numeric_cols = [
            config.TRADER_COL_EXEC_PRICE,
            config.TRADER_COL_SIZE_TOKENS,
            config.TRADER_COL_SIZE_USD,
            config.TRADER_COL_START_POS,
            config.TRADER_COL_CLOSED_PNL,
            config.TRADER_COL_FEE
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
        # Parse Timestamps
        # The 'Timestamp IST' column is standard string e.g. 02-12-2024 22:50 (Day-Month-Year Hour:Minute)
        # The 'Timestamp' column is Unix epoch in ms (often in scientific notation, e.g., 1.73E+12)
        # We parse the 'Timestamp IST' as it has exact minutes and fits timezone logic.
        df['datetime_ist'] = pd.to_datetime(df[config.TRADER_COL_TS_IST], format='%d-%m-%Y %H:%M', errors='coerce')
        
        # For rows where IST parsing fails, try parsing 'Timestamp' (epoch ms)
        failed_ist = df['datetime_ist'].isna()
        if failed_ist.any():
            logger.info(f"Falling back to epoch timestamp parsing for {failed_ist.sum()} rows where IST parsing failed")
            # Parse scientific notation to float first
            epochs = pd.to_numeric(df.loc[failed_ist, config.TRADER_COL_TS], errors='coerce')
            # Convert epoch ms to datetime (UTC) and then convert to IST (UTC+5:30)
            parsed_epochs = pd.to_datetime(epochs, unit='ms', utc=True, errors='coerce')
            df.loc[failed_ist, 'datetime_ist'] = parsed_epochs.dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
            
        # Create a date-only column for daily merging
        df['date'] = df['datetime_ist'].dt.date
        df['date'] = pd.to_datetime(df['date']) # keep as pandas datetime
        
        # Strip coin labels (remove @ indices if required, or keep them)
        df[config.TRADER_COL_COIN] = df[config.TRADER_COL_COIN].astype(str).str.strip()
        
        # Drop rows where datetime_ist is completely missing
        num_before = df.shape[0]
        df = df.dropna(subset=['datetime_ist'])
        num_after = df.shape[0]
        if num_before != num_after:
            logger.warning(f"Dropped {num_before - num_after} rows due to unparseable timestamps")
            
        # Sort by timestamp
        df = df.sort_values(by='datetime_ist').reset_index(drop=True)
        
        logger.info(f"Successfully loaded Trader Data: {df.shape[0]} rows, date range {df['datetime_ist'].min()} to {df['datetime_ist'].max()}")
        return df
    except Exception as e:
        logger.error(f"Error loading Trader dataset: {e}")
        raise

if __name__ == "__main__":
    # Quick sanity check run
    fg_df = load_fear_greed_data()
    trader_df = load_trader_data()
    print("Fear & Greed columns:", fg_df.columns.tolist())
    print("Trader columns:", trader_df.columns.tolist())
