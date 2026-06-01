# Bitcoin Market Sentiment & Hyperliquid Trader Behavior Analysis

This project explores the relationship between trader performance (Hyperliquid transaction logs) and Bitcoin market sentiment (Fear & Greed Index). We analyze 211,224 transactions from 32 unique traders across 246 coins over a 2-year overlapping window (May 2023 to May 2025).

---

## 1. Project Objectives
*   **Ingest and clean** large-scale trader execution logs and daily sentiment values.
*   **Profile trader cohorts** (Difference Between Large and Small Traders, Profitable vs. Unprofitable) based on trading volume, frequency, win rate, and profit factor.
*   **Map transactions to sentiment cycles** to study behavioral changes under different market conditions (Extreme Fear, Fear, Neutral, Greed, Extreme Greed).
*   **Evaluate Buying vs. Selling Balance** using the *Buying vs. Selling Balance (Net Buy Volume Ratio)*.

---

## 2. Project Structure
```text
PTAI-assesment/
├── .gitignore
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py           # Config variables (paths, column maps)
│   ├── data_loader.py      # Loaders for F&G and Hyperliquid datasets
│   ├── metrics.py          # Trader and coin metrics calculations
│   ├── sentiment.py        # Sentiment merging and regime mapping logic
│   └── visualizer.py       # Basic Matplotlib plot generators
├── notebooks/
│   └── exploratory_analysis.ipynb # Jupyter Notebook presenting findings
└── outputs/
    └── plots/              # Folder for saved figure images
        ├── regime_distribution.png
        ├── cohort_performance_regime.png
        ├── cumulative_pnl_over_time.png
        └── net_buy_ratio_regime.png
```

---

## 3. Environment & Execution Setup

### Step 1: Create a virtual environment
```bash
python3 -m venv .venv
```

### Step 2: Activate the environment & install dependencies
On macOS/Linux:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```
On Windows:
```cmd
.venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Run the Analysis Jupyter Notebook
Ensure you are in the virtual environment, then start Jupyter:
```bash
jupyter notebook
```
Navigate to `notebooks/exploratory_analysis.ipynb` and run all cells. This notebook will load the datasets, run the profiling scripts, save the figures, and display the results inline.

---

## 4. Summary of Key Insights

### 1. Difference Between Large and Small Traders
*   **How Small Traders Behave in Different Market Conditions**: Small traders trade much less when the market is panicking (only 871 trades during `Extreme Fear`) compared to when things are going up (`Greed`: 1,975 trades). When they do try to trade during extreme panic, their win rate drops to a low **42.9%**, showing they struggle to time the market bottoms.
*   **How Large Traders Behave in Different Market Conditions**: Large traders keep execution active no matter what. They made over 13,000 trades during Extreme Fear and kept a high win rate of **79.8%**. They also made their biggest absolute Net Profits (Profit) during `Extreme Greed` (+$1.67M), taking advantage of high market excitement.

### 2. Trading Behavior Patterns (Buying vs. Selling Balance)
The **Buying vs. Selling Balance** (Net Buy Volume Ratio) is defined as:
$$\text{Net Buy Ratio} = \frac{\text{BUY Volume} - \text{SELL Volume}}{\text{Total Volume}}$$

*   **Following Market Trends & Poor Performance During Market Fear**: During Extreme Fear, retail traders are mostly buying (a positive Buying vs. Selling Balance of +0.36), but since their win rate is so low, they are likely buying assets that are still falling. During greedy markets, they net sell (-0.63), showing they take profit too early and miss out on bigger trends.
*   **Consistent Market-Making Strategy & Balanced Trading Strategy**: The most interesting finding is that the large traders have a Buying vs. Selling Balance (Net Buy Ratio) very close to zero (-0.03 to +0.06) across all market conditions. This means their buys and sells are almost perfectly equal. They are likely running automated market-making algorithms that don't try to predict where the price is going, but instead provide liquidity and collect trading fees.
