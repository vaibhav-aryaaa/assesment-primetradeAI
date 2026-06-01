import pandas as pd
import numpy as np
import logging
from src import config

logger = logging.getLogger(__name__)

# Standard ordered categories for Fear & Greed classifications
REGIME_ORDER = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']

def merge_trader_and_sentiment_data(trader_df, fg_df):
    """
    Merges transaction logs with the daily Fear and Greed index on the 'date' column.
    """
    logger.info("Merging trader transactions with Fear & Greed Index...")
    
    # Ensure both dataframes have the date column as datetime64
    trader_df = trader_df.copy()
    fg_df = fg_df.copy()
    
    trader_df['date'] = pd.to_datetime(trader_df['date'])
    fg_df['date'] = pd.to_datetime(fg_df['date'])
    
    # Left join to preserve all trader records
    merged_df = pd.merge(
        trader_df, 
        fg_df[[config.FG_COL_DATE, config.FG_COL_VAL, config.FG_COL_CLASS]], 
        on='date', 
        how='left'
    )
    
    # Fill any missing classification/value with 'Neutral' or standard defaults
    merged_df[config.FG_COL_CLASS] = merged_df[config.FG_COL_CLASS].fillna('Neutral')
    merged_df[config.FG_COL_VAL] = merged_df[config.FG_COL_VAL].fillna(50.0)
    
    # Cast classification as an ordered categorical variable
    merged_df[config.FG_COL_CLASS] = pd.Categorical(
        merged_df[config.FG_COL_CLASS],
        categories=REGIME_ORDER,
        ordered=True
    )
    
    logger.info(f"Successfully merged data. Shape: {merged_df.shape}")
    return merged_df

def analyze_by_sentiment_regime(merged_df, trader_metrics_df=None):
    """
    Aggregates transaction volumes, PnL, and frequency by sentiment regime.
    If trader_metrics_df is provided, aggregates stats by cohorts (Whale/Retail, etc.).
    """
    logger.info("Analyzing trader behavior across sentiment regimes...")
    
    # Ensure transaction flags are set
    merged_df = merged_df.copy()
    merged_df['is_realized'] = merged_df[config.TRADER_COL_CLOSED_PNL] != 0
    merged_df['is_win'] = merged_df[config.TRADER_COL_CLOSED_PNL] > 0
    
    # 1. Overall Regime Aggregation
    regime_stats = merged_df.groupby(config.FG_COL_CLASS, observed=False).agg(
        total_pnl=(config.TRADER_COL_CLOSED_PNL, 'sum'),
        total_volume=(config.TRADER_COL_SIZE_USD, 'sum'),
        total_fees=(config.TRADER_COL_FEE, 'sum'),
        trade_count=('Account', 'count'),
        realized_trades=('is_realized', 'sum'),
        winning_trades=('is_win', 'sum')
    ).reset_index()
    
    regime_stats['net_pnl'] = regime_stats['total_pnl'] - regime_stats['total_fees']
    regime_stats['win_rate'] = np.where(
        regime_stats['realized_trades'] > 0,
        regime_stats['winning_trades'] / regime_stats['realized_trades'],
        0.0
    )
    regime_stats['avg_trade_size'] = np.where(
        regime_stats['trade_count'] > 0,
        regime_stats['total_volume'] / regime_stats['trade_count'],
        0.0
    )
    
    results = {
        'overall': regime_stats
    }
    
    # 2. Cohort-wise Regime Aggregation (if trader_metrics is provided)
    if trader_metrics_df is not None:
        logger.info("Performing cohort breakdown by sentiment regime...")
        # Map cohorts from account metrics back to transaction level
        account_map = trader_metrics_df.set_index('Account')
        
        merged_df['volume_cohort'] = merged_df[config.TRADER_COL_ACCOUNT].map(account_map['volume_cohort'])
        merged_df['profit_cohort'] = merged_df[config.TRADER_COL_ACCOUNT].map(account_map['profit_cohort'])
        
        # Aggregate by Volume Cohort and Sentiment Regime
        vol_cohort_stats = merged_df.groupby(['volume_cohort', config.FG_COL_CLASS], observed=False).agg(
            total_pnl=(config.TRADER_COL_CLOSED_PNL, 'sum'),
            total_volume=(config.TRADER_COL_SIZE_USD, 'sum'),
            total_fees=(config.TRADER_COL_FEE, 'sum'),
            trade_count=('Account', 'count'),
            realized_trades=('is_realized', 'sum'),
            winning_trades=('is_win', 'sum')
        ).reset_index()
        
        vol_cohort_stats['net_pnl'] = vol_cohort_stats['total_pnl'] - vol_cohort_stats['total_fees']
        vol_cohort_stats['win_rate'] = np.where(
            vol_cohort_stats['realized_trades'] > 0,
            vol_cohort_stats['winning_trades'] / vol_cohort_stats['realized_trades'],
            0.0
        )
        
        results['volume_cohort'] = vol_cohort_stats
        
        # Aggregate by Profitability Cohort and Sentiment Regime
        profit_cohort_stats = merged_df.groupby(['profit_cohort', config.FG_COL_CLASS], observed=False).agg(
            total_pnl=(config.TRADER_COL_CLOSED_PNL, 'sum'),
            total_volume=(config.TRADER_COL_SIZE_USD, 'sum'),
            total_fees=(config.TRADER_COL_FEE, 'sum'),
            trade_count=('Account', 'count'),
            realized_trades=('is_realized', 'sum'),
            winning_trades=('is_win', 'sum')
        ).reset_index()
        
        profit_cohort_stats['net_pnl'] = profit_cohort_stats['total_pnl'] - profit_cohort_stats['total_fees']
        profit_cohort_stats['win_rate'] = np.where(
            profit_cohort_stats['realized_trades'] > 0,
            profit_cohort_stats['winning_trades'] / profit_cohort_stats['realized_trades'],
            0.0
        )
        
        results['profit_cohort'] = profit_cohort_stats
        
    return results
