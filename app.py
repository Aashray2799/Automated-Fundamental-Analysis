import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup

# Set Streamlit layout
st.set_page_config(page_title="Automated Fundamental Analysis", layout="wide")

# --- Function to compute Overall Rating ---
def compute_overall_rating(df):
    # First, convert numeric columns safely
    numeric_cols = ['P/E', 'Price', 'Change', 'Volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].str.replace('%', '').str.replace(',', ''), errors='coerce')

    # Normalize and score each column (example logic)
    df['Valuation_Score'] = df['P/E'].rank(pct=True, ascending=True)  # lower P/E is better
    df['Momentum_Score'] = df['Change'].rank(pct=True, ascending=False)  # higher change is better
    df['Volume_Score'] = df['Volume'].rank(pct=True, ascending=False)

    # Combine scores into an overall rating
    df['Overall Rating'] = ((df['Valuation_Score'] + df['Momentum_Score'] + df['Volume_Score']) / 3).round(2)

    return df
# --- Fetch Data ---
@st.cache_data(ttl=3600)
def fetch_data_from_finviz(pages=1):
    headers = {"User-Agent": "Mozilla/5.0"}
    base_url = "https://finviz.com/screener.ashx?v=111&f=idx_sp500"
    
    all_data = []

    for page in range(pages):
        url = f"{base_url}&r={page * 20 + 1}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")

        table = soup.find("table", class_="screener-view-table")
        rows = table.find_all("tr")[1:]

        for row in rows:
            cols = [td.text.strip() for td in row.find_all("td")]
            if cols:
                all_data.append(cols)

    columns = [
        "No", "Ticker", "Company", "Sector", "Industry", "Country",
        "Market Cap", "P/E", "Price", "Change", "Volume"
    ]

    df = pd.DataFrame(all_data, columns=columns)
    return df

# --- Title ---
st.title("📊 Automated Fundamental Analysis")

st.markdown("""
Analyze **8,000+ stocks** based on valuation, profitability, growth, and price performance—**relative to their sector**.

Data Source: Finviz  
Dataset: `StockRatings-04.05.22.csv`
""")

# --- Refresh button ---
if st.button("🔄 Refresh Live Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# --- Load Data ---
try:
    df = fetch_data_from_finviz(pages=5)  # Loads 40 stocks (2 pages)
    df = compute_overall_rating(df)       # Compute rating
except Exception as e:
    st.error(f"❌ Failed to fetch data from Finviz:\n\n{e}")
    st.stop()

# --- Sidebar Columns ---
st.sidebar.subheader("📋 Available Columns")
st.sidebar.write(df.columns.tolist())

available_metrics = ['P/E', 'Price', 'Change', 'Volume', 'Overall Rating']

# --- Validate Required Columns ---
required_cols = ['Ticker', 'Company', 'Price', 'Market Cap', 'Sector', 'Industry', 'Overall Rating']
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.write("Columns in DataFrame:", df.columns.tolist())  # Debug help
    st.stop()

# --- Ticker Analysis ---
st.header("🔍 Ticker Lookup")
ticker = st.selectbox("Select a Ticker", df['Ticker'].unique())
df['Ticker'] = df['Ticker'].str.strip().str.upper()
st.sidebar.text("Tickers:\n" + "\n".join(df['Ticker'].dropna().unique().tolist()))
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

    # Analysis block
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

sectors = sorted(df['Sector'].dropna().unique())
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

# --- Grading System ---
st.markdown("---")
st.header("📘 Grading System")

st.markdown("""
The grading system compares a stock's metric within its **sector or industry** and calculates:

- 📊 Mean of the group  
- 🏁 90th Percentile  
- 📉 Change = (Std. Dev / 3)
""")

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

    # Convert grades if needed
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
