import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging
from src import config

logger = logging.getLogger(__name__)

def generate_and_save_plots(merged_df, trader_metrics_df, regime_results):
    """
    Generates 4 basic, simple matplotlib plots and saves them to the outputs/plots/ directory.
    No custom styling, just clean standard matplotlib plots.
    """
    # Create output directories if they do not exist
    os.makedirs(config.PLOTS_DIR, exist_ok=True)
    logger.info(f"Generating and saving basic plots to {config.PLOTS_DIR}")
    
    # Extract dataframes from regime results
    overall = regime_results['overall']
    vol_cohort = regime_results['volume_cohort']
    
    # Plot 1: Regime Distribution (Trade Count & Volume)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Trade Count
    ax1.bar(overall['classification'].astype(str), overall['trade_count'], color='blue', alpha=0.7)
    ax1.set_title("Total Trades by Sentiment Regime")
    ax1.set_xlabel("Sentiment Regime")
    ax1.set_ylabel("Number of Trades")
    ax1.set_xticks(range(len(overall)))
    ax1.set_xticklabels(overall['classification'].astype(str), rotation=30)
    
    # Volume
    ax2.bar(overall['classification'].astype(str), overall['total_volume'] / 1e6, color='green', alpha=0.7)
    ax2.set_title("Total Trading Volume by Sentiment Regime (in Millions USD)")
    ax2.set_xlabel("Sentiment Regime")
    ax2.set_ylabel("Volume ($M USD)")
    ax2.set_xticks(range(len(overall)))
    ax2.set_xticklabels(overall['classification'].astype(str), rotation=30)
    
    plt.tight_layout()
    plot1_path = os.path.join(config.PLOTS_DIR, "regime_distribution.png")
    plt.savefig(plot1_path)
    plt.close()
    logger.info(f"Saved: {plot1_path}")
    
    # Plot 2: Cohort Performance by Regime (Win Rate & Net PnL)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    regimes = overall['classification'].astype(str).tolist()
    x = np.arange(len(regimes))
    width = 0.35
    
    # Filter cohorts for Whale and Retail
    whale_stats = vol_cohort[vol_cohort['volume_cohort'] == 'Whale'].set_index('classification').reindex(regimes).reset_index()
    retail_stats = vol_cohort[vol_cohort['volume_cohort'] == 'Retail'].set_index('classification').reindex(regimes).reset_index()
    
    # Grouped Bar: Win Rate
    ax1.bar(x - width/2, whale_stats['win_rate'], width, label='Whale', color='blue')
    ax1.bar(x + width/2, retail_stats['win_rate'], width, label='Retail', color='orange')
    ax1.set_title("Win Rate by Sentiment Regime")
    ax1.set_xlabel("Sentiment Regime")
    ax1.set_ylabel("Win Rate (%)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(regimes, rotation=30)
    ax1.legend()
    
    # Grouped Bar: Net PnL
    ax2.bar(x - width/2, whale_stats['net_pnl'] / 1e3, width, label='Whale', color='blue')
    ax2.bar(x + width/2, retail_stats['net_pnl'] / 1e3, width, label='Retail', color='orange')
    ax2.set_title("Net PnL by Sentiment Regime (in Thousands USD)")
    ax2.set_xlabel("Sentiment Regime")
    ax2.set_ylabel("Net PnL ($K USD)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(regimes, rotation=30)
    ax2.legend()
    
    plt.tight_layout()
    plot2_path = os.path.join(config.PLOTS_DIR, "cohort_performance_regime.png")
    plt.savefig(plot2_path)
    plt.close()
    logger.info(f"Saved: {plot2_path}")
    
    # Plot 3: Cumulative Net PnL Over Time
    plt.figure(figsize=(10, 6))
    
    # Map account volume cohort back to transaction data
    merged_df = merged_df.copy()
    account_cohort_map = trader_metrics_df.set_index('Account')['volume_cohort'].to_dict()
    merged_df['volume_cohort'] = merged_df[config.TRADER_COL_ACCOUNT].map(account_cohort_map)
    
    # Calculate net pnl per transaction
    merged_df['tx_net_pnl'] = merged_df[config.TRADER_COL_CLOSED_PNL] - merged_df[config.TRADER_COL_FEE]
    
    # Group by date and cohort, sum PnL
    daily_pnl = merged_df.groupby(['date', 'volume_cohort'])['tx_net_pnl'].sum().unstack().fillna(0.0)
    
    # Calculate cumulative PnL
    cumulative_pnl = daily_pnl.cumsum()
    
    for cohort in ['Whale', 'Medium', 'Retail']:
        if cohort in cumulative_pnl.columns:
            plt.plot(cumulative_pnl.index, cumulative_pnl[cohort] / 1e6, label=cohort, linewidth=2)
            
    plt.title("Cumulative Net PnL Over Time by Volume Cohort")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Net PnL ($M USD)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.xticks(rotation=30)
    
    plt.tight_layout()
    plot3_path = os.path.join(config.PLOTS_DIR, "cumulative_pnl_over_time.png")
    plt.savefig(plot3_path)
    plt.close()
    logger.info(f"Saved: {plot3_path}")
    
    # Plot 4: BUY vs. SELL Volume (Net Buy Ratio)
    plt.figure(figsize=(8, 5))
    
    # Compute Net Buy Ratio = (BUY - SELL) / (BUY + SELL)
    vol_by_side = merged_df.groupby(['volume_cohort', 'classification', 'Side'], observed=False)['Size USD'].sum().unstack(fill_value=0.0).reset_index()
    vol_by_side['net_buy_ratio'] = (vol_by_side['BUY'] - vol_by_side['SELL']) / (vol_by_side['BUY'] + vol_by_side['SELL'])
    
    # Extract for plotting
    x = np.arange(len(regimes))
    width = 0.35
    
    whale_ratios = vol_by_side[vol_by_side['volume_cohort'] == 'Whale'].set_index('classification').reindex(regimes)['net_buy_ratio'].fillna(0.0)
    retail_ratios = vol_by_side[vol_by_side['volume_cohort'] == 'Retail'].set_index('classification').reindex(regimes)['net_buy_ratio'].fillna(0.0)
    
    plt.bar(x - width/2, whale_ratios, width, label='Whale Ratios', color='blue')
    plt.bar(x + width/2, retail_ratios, width, label='Retail Ratios', color='orange')
    
    plt.title("Net Buy Volume Ratio by Sentiment Regime")
    plt.xlabel("Sentiment Regime")
    plt.ylabel("Net Buy Ratio (Positive = BUY, Negative = SELL)")
    plt.xticks(x, regimes, rotation=30)
    plt.axhline(0, color='black', linewidth=1, linestyle='--')
    plt.legend()
    
    plt.tight_layout()
    plot4_path = os.path.join(config.PLOTS_DIR, "net_buy_ratio_regime.png")
    plt.savefig(plot4_path)
    plt.close()
    logger.info(f"Saved: {plot4_path}")
