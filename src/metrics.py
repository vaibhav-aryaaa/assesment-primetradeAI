import pandas as pd
import numpy as np
import logging
from src import config

logger = logging.getLogger(__name__)

def calculate_trader_metrics(df):
    """
    Aggregates transaction-level data to calculate account-level performance metrics.
    Categorizes accounts into cohorts based on volume, activity, and profitability.
    """
    logger.info("Calculating trader performance metrics...")
    
    # Pre-calculate winning and losing flags
    df = df.copy()
    df['is_realized'] = df[config.TRADER_COL_CLOSED_PNL] != 0
    df['is_win'] = df[config.TRADER_COL_CLOSED_PNL] > 0
    df['is_loss'] = df[config.TRADER_COL_CLOSED_PNL] < 0
    
    # Group by account and aggregate metrics
    grouped = df.groupby(config.TRADER_COL_ACCOUNT)
    
    metrics = grouped.agg(
        total_pnl=(config.TRADER_COL_CLOSED_PNL, 'sum'),
        total_volume=(config.TRADER_COL_SIZE_USD, 'sum'),
        total_fees=(config.TRADER_COL_FEE, 'sum'),
        trade_count=(config.TRADER_COL_ACCOUNT, 'count'),
        realized_trades=('is_realized', 'sum'),
        winning_trades=('is_win', 'sum'),
        losing_trades=('is_loss', 'sum')
    ).reset_index()
    
    # Net PnL (Gross PnL minus Fees)
    metrics['net_pnl'] = metrics['total_pnl'] - metrics['total_fees']
    
    # Win Rate: winning realized trades / total realized trades
    metrics['win_rate'] = np.where(
        metrics['realized_trades'] > 0,
        metrics['winning_trades'] / metrics['realized_trades'],
        0.0
    )
    
    # Average Trade Size
    metrics['average_trade_size'] = np.where(
        metrics['trade_count'] > 0,
        metrics['total_volume'] / metrics['trade_count'],
        0.0
    )
    
    # Profit Factor: sum of profits / absolute sum of losses
    # We calculate the sum of positive PnL and absolute sum of negative PnL per account
    profits = df[df['is_win']].groupby(config.TRADER_COL_ACCOUNT)[config.TRADER_COL_CLOSED_PNL].sum()
    losses = df[df['is_loss']].groupby(config.TRADER_COL_ACCOUNT)[config.TRADER_COL_CLOSED_PNL].sum().abs()
    
    # Map back to the metrics dataframe
    metrics['gross_profits'] = metrics[config.TRADER_COL_ACCOUNT].map(profits).fillna(0.0)
    metrics['gross_losses'] = metrics[config.TRADER_COL_ACCOUNT].map(losses).fillna(0.0)
    
    metrics['profit_factor'] = np.where(
        metrics['gross_losses'] > 0,
        metrics['gross_profits'] / metrics['gross_losses'],
        np.where(metrics['gross_profits'] > 0, 99.9, 1.0) # Handle no losses case
    )
    
    # Drop intermediate columns
    metrics = metrics.drop(columns=['gross_profits', 'gross_losses'])
    
    # Cohort Categorizations (based on dataset quantiles)
    # 1. Volume Cohorts: Whale (Top 25% >= $35M), Medium (Middle 50%), Retail (Bottom 25% < $4M)
    metrics['volume_cohort'] = pd.cut(
        metrics['total_volume'],
        bins=[-np.inf, 4_000_000, 35_000_000, np.inf],
        labels=['Retail', 'Medium', 'Whale']
    ).astype(str)
    
    # 2. Activity Cohorts: High (Top 25% >= 10k trades), Medium (Middle 50%), Low (Bottom 25% < 2k trades)
    metrics['activity_cohort'] = pd.cut(
        metrics['trade_count'],
        bins=[-np.inf, 2_000, 10_000, np.inf],
        labels=['Low', 'Medium', 'High']
    ).astype(str)
    
    # 3. Profitability Cohorts: Profitable (Net PnL > 0) vs Unprofitable
    metrics['profit_cohort'] = np.where(
        metrics['net_pnl'] > 0,
        'Profitable',
        'Unprofitable'
    )
    
    logger.info(f"Successfully calculated metrics for {metrics.shape[0]} accounts.")
    return metrics

def calculate_coin_metrics(df):
    """
    Aggregates transaction-level data to calculate coin-level metrics.
    """
    logger.info("Calculating coin-level metrics...")
    
    grouped = df.groupby(config.TRADER_COL_COIN)
    
    coin_stats = grouped.agg(
        total_pnl=(config.TRADER_COL_CLOSED_PNL, 'sum'),
        total_volume=(config.TRADER_COL_SIZE_USD, 'sum'),
        total_fees=(config.TRADER_COL_FEE, 'sum'),
        trade_count=(config.TRADER_COL_COIN, 'count')
    ).reset_index()
    
    # Sort by total volume descending
    coin_stats = coin_stats.sort_values(by='total_volume', ascending=False).reset_index(drop=True)
    
    logger.info(f"Successfully calculated metrics for {coin_stats.shape[0]} coins.")
    return coin_stats
