import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf

# --- Tickers ---
sp500_tickers = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    'TSLA', 'BRK-B', 'JPM', 'JNJ', 'V',
    'PG', 'XOM', 'UNH', 'NVDA', 'HD',
    'CVX', 'MA', 'ABBV', 'PEP', 'LLY'
]

# --- Fetch Data from Yahoo ---
@st.cache_data(ttl=3600)
def fetch_data_from_yahoo(tickers, batch_size=10):
    all_data = []
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        data = yf.Tickers(' '.join(batch)).tickers
        for ticker in batch:
            info = data[ticker].info
            try:
                all_data.append({
                    'Ticker': ticker,
                    'Company': info.get('shortName', ''),
                    'Sector': info.get('sector', ''),
                    'Industry': info.get('industry', ''),
                    'Market Cap': info.get('marketCap', ''),
                    'P/E': info.get('trailingPE', ''),
                    'Price': info.get('currentPrice', ''),
                    'Change': info.get('regularMarketChangePercent', 0) * 100,
                    'Volume': info.get('volume', '')
                })
            except Exception:
                continue
    return pd.DataFrame(all_data)

# --- Compute Overall Rating ---
def compute_overall_rating(df):
    numeric_cols = ['P/E', 'Price', 'Change', 'Volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Valuation_Score'] = df['P/E'].rank(pct=True, ascending=True)
    df['Momentum_Score'] = df['Change'].rank(pct=True, ascending=False)
    df['Volume_Score'] = df['Volume'].rank(pct=True, ascending=False)
    df['Overall Rating'] = ((df['Valuation_Score'] + df['Momentum_Score'] + df['Volume_Score']) / 3).round(2)
    return df

# --- Page Setup ---
st.set_page_config(page_title="📊 Automated Fundamental Analysis", layout="wide")

st.title("📊 Automated Fundamental Analysis")
st.markdown("💹 **With tariffs shaking up the market, it's the perfect time to compare top S&P 500 stocks — by value, growth, and momentum.**")

# --- Refresh Button ---
if st.button("🔄 Refresh Live Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# --- Load Data ---
try:
    df = fetch_data_from_yahoo(sp500_tickers)
    df = compute_overall_rating(df)
    df['Ticker'] = df['Ticker'].str.strip().str.upper()
except Exception as e:
    st.error(f"❌ Failed to fetch data from Yahoo Finance:\n\n{e}")
    st.stop()

# --- Sidebar ---
st.sidebar.subheader("📋 Available Columns")
st.sidebar.write(df.columns.tolist())
st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 Created by [Nikhil Konda](https://github.com/aashray27999)")

available_metrics = ['P/E', 'Price', 'Change', 'Volume', 'Overall Rating']

# --- Ticker Analysis ---
st.header("🔍 Ticker Lookup")
ticker = st.selectbox("Select a Ticker", df['Ticker'].unique())
if ticker in df['Ticker'].values:
    stock = df[df['Ticker'] == ticker].iloc[0]

    st.subheader(f"{stock['Company']} ({ticker})")
    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${stock['Price']}")
    col2.metric("Market Cap", f"{stock['Market Cap']}")
    col3.metric("Overall Rating", stock.get('Overall Rating', 'N/A'))

    col4, col5 = st.columns(2)
    col4.metric("Sector", stock['Sector'])
    col5.metric("Industry", stock['Industry'])

    # --- Metric Distribution ---
    st.markdown("### 📈 Analyze a Metric")
    selected_metric = st.selectbox("Pick a metric to analyze", available_metrics)
    analysis_scope = st.radio("Analyze by", ["Sector", "Industry"])
    group = stock[analysis_scope]
    scoped_df = df[df[analysis_scope] == group]

    fig, ax = plt.subplots()
    sns.histplot(scoped_df[selected_metric], kde=True, ax=ax)
    ax.axvline(stock[selected_metric], color='red', linestyle='--', label=ticker)
    ax.set_title(f"{selected_metric} Distribution in {group} {analysis_scope}")
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("Ticker not found in dataset.")

# --- Sector Comparison ---
st.markdown("---")
st.header("🏆 Compare Sectors")

sectors = sorted(df['Sector'].dropna().unique().tolist())
if len(sectors) >= 2:
    sector1 = st.selectbox("Select Sector", sectors)
    sector2 = st.selectbox("Select a Sector to Compare", sectors, index=1 if sectors[0] == sector1 else 0)
    comparison_metric = st.selectbox("Select a Metric", available_metrics, key="compare_metric")

    df1 = df[df['Sector'] == sector1]
    df2 = df[df['Sector'] == sector2]

    fig2, ax2 = plt.subplots()
    sns.kdeplot(df1[comparison_metric], fill=True, label=sector1, alpha=0.5)
    sns.kdeplot(df2[comparison_metric], fill=True, label=sector2, alpha=0.5)
    ax2.set_title(f"{comparison_metric} Distribution: {sector1} vs {sector2}")
    ax2.legend()
    st.pyplot(fig2)
elif len(sectors) == 1:
    st.info("Only one sector available.")
else:
    st.warning("⚠️ No sector data found.")

# --- Grading System ---
st.markdown("---")
st.header("📘 Grading System")

grading_metric = st.selectbox("Select Metric for Grading Breakdown", available_metrics, key="grading")
grading_scope = st.radio("Grading Scope", ["Sector", "Industry"], horizontal=True)

if ticker in df['Ticker'].values and grading_metric in df.columns:
    group = stock[grading_scope]
    grading_df = df[df[grading_scope] == group]

    grade_map = {
        'A+': 10, 'A': 9, 'A-': 8,
        'B+': 7, 'B': 6, 'B-': 5,
        'C+': 4, 'C': 3, 'C-': 2,
        'D+': 1, 'D': 0
    }

    raw_values = grading_df[grading_metric].dropna()
    if raw_values.dtype == 'object':
        values = raw_values.map(grade_map)
        stock_val = grade_map.get(stock[grading_metric], None)
    else:
        values = raw_values
        stock_val = stock[grading_metric]

    if stock_val is not None:
        mean_val = values.mean()
        p90_val = values.quantile(0.9)
        std_val = values.std()
        change_val = std_val / 3

        st.markdown(f"""
        ```
        {group} {grading_metric} Avg: {mean_val:.2f}
        90th Percentile: {p90_val:.3f}
        Change: {change_val:.4f}
        ```
        """)

        fig3, ax3 = plt.subplots()
        sns.histplot(values, kde=True, bins=25, ax=ax3, color='skyblue')
        ax3.axvline(mean_val, color='blue', linestyle='--', label='Mean')
        ax3.axvline(p90_val, color='green', linestyle='--', label='90th Percentile')
        ax3.axvline(stock_val, color='red', linestyle='-', label=ticker)
        ax3.set_title(f"{grading_metric} Distribution in {group} {grading_scope}")
        ax3.legend()
        st.pyplot(fig3)
    else:
        st.error("⚠️ Could not convert the selected stock's grade into a number.")
