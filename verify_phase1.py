#!/usr/bin/env python3
import os
import sys

# Ensure project root is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_fear_greed_data, load_trader_data
from src import config

def main():
    print("=========================================")
    print("PHASE 1: DATA INGESTION & SANITY CHECK")
    print("=========================================\n")

    # 1. Load Bitcoin Fear & Greed Index
    print("--- 1. Loading Bitcoin Fear & Greed Index ---")
    fg_df = load_fear_greed_data()
    print(f"Shape: {fg_df.shape}")
    print(f"Columns: {fg_df.columns.tolist()}")
    print(f"Date range: {fg_df[config.FG_COL_DATE].min().strftime('%Y-%m-%d')} to {fg_df[config.FG_COL_DATE].max().strftime('%Y-%m-%d')}")
    print(f"Null values check:\n{fg_df.isnull().sum()}\n")
    print("First 3 rows preview:")
    print(fg_df.head(3))
    print("\n-----------------------------------------\n")

    # 2. Load Historical Trader Data
    print("--- 2. Loading Hyperliquid Historical Trader Data ---")
    trader_df = load_trader_data()
    print(f"Shape: {trader_df.shape}")
    print(f"Columns: {trader_df.columns.tolist()}")
    print(f"Date range (IST): {trader_df['datetime_ist'].min()} to {trader_df['datetime_ist'].max()}")
    print(f"Unique accounts: {trader_df[config.TRADER_COL_ACCOUNT].nunique()}")
    print(f"Unique coins traded: {trader_df[config.TRADER_COL_COIN].nunique()}")
    print(f"Null values check:\n{trader_df.isnull().sum()}\n")
    print("First 2 rows preview:")
    # Drop some hash columns in print to make it readable in console
    preview_cols = [
        config.TRADER_COL_ACCOUNT, config.TRADER_COL_COIN, 
        config.TRADER_COL_EXEC_PRICE, config.TRADER_COL_SIZE_USD, 
        config.TRADER_COL_SIDE, config.TRADER_COL_TS_IST, 
        config.TRADER_COL_CLOSED_PNL, 'datetime_ist'
    ]
    print(trader_df[preview_cols].head(2))
    print("\n-----------------------------------------\n")

    # 3. Check Date Overlaps
    print("--- 3. Checking Date Overlaps ---")
    fg_min_date = fg_df[config.FG_COL_DATE].min()
    fg_max_date = fg_df[config.FG_COL_DATE].max()
    trader_min_date = trader_df['date'].min()
    trader_max_date = trader_df['date'].max()
    
    overlap_min = max(fg_min_date, trader_min_date)
    overlap_max = min(fg_max_date, trader_max_date)
    
    print(f"Fear & Greed Index Range: {fg_min_date.date()} to {fg_max_date.date()}")
    print(f"Hyperliquid Trader Range: {trader_min_date.date()} to {trader_max_date.date()}")
    
    if overlap_min <= overlap_max:
        print(f"Overlapping period: {overlap_min.date()} to {overlap_max.date()}")
        # Calculate how many trader rows fall in the overlap
        in_overlap = trader_df['date'].between(overlap_min, overlap_max).sum()
        print(f"Trader rows within overlap period: {in_overlap} ({in_overlap/len(trader_df)*100:.2f}%)")
    else:
        print("WARNING: No overlapping period found between the two datasets!")
    
    print("\n=========================================")
    print("PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY")
    print("=========================================")

if __name__ == "__main__":
    main()
