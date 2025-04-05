import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit layout
st.set_page_config(page_title="Automated Fundamental Analysis", layout="wide")

# Title
st.title("📊 Automated Fundamental Analysis")

# Description
st.markdown("""
Analyze **8,000+ stocks** based on valuation, profitability, growth, and price performance—**relative to their sector**.

Data Source: Finviz  
Dataset: `StockRatings-04.05.22.csv`
""")

# Load dataset
try:
    df = pd.read_csv("StockRatings-04.05.22.csv")
except Exception as e:
    st.error(f"❌ Could not load StockRatings-04.05.22.csv\n\n{e}")
    st.stop()

# Show columns in sidebar
st.sidebar.subheader("📋 Available Columns")
st.sidebar.write(df.columns.tolist())

# Validate key columns
required_cols = ['Ticker', 'Company', 'Price', 'Market Cap', 'Sector', 'Industry', 'Overall Rating']
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.stop()

# --- Ticker Analysis ---
st.header("🔍 Ticker Lookup")
ticker = st.text_input("Enter a Ticker Symbol", value="AAPL").upper()

if ticker in df['Ticker'].values:
    stock = df[df['Ticker'] == ticker].iloc[0]

    st.subheader(f"{stock['Company']} ({ticker})")
    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${stock['Price']}")
    col2.metric("Market Cap", f"{stock['Market Cap']}B")
    col3.metric("Overall Rating", stock['Overall Rating'])

    col4, col5 = st.columns(2)
    col4.metric("Sector", stock['Sector'])
    col5.metric("Industry", stock['Industry'])

    metric_options = ['Overall Rating', 'Valuation', 'Profitability', 'Growth', 'Performance']
    available_metrics = [m for m in metric_options if m in df.columns]

    st.markdown("### 📈 Analyze a Metric")
    selected_metric = st.selectbox("Pick a metric to analyze", available_metrics)
    analysis_scope = st.radio("Analyze by", ["Sector", "Industry"])
    group = stock[analysis_scope]
    scoped_df = df[df[analysis_scope] == group]

    # Plot distribution
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

    values = grading_df[grading_metric].dropna()
    mean_val = values.mean()
    p90_val = values.quantile(0.9)
    std_val = values.std()
    change_val = std_val / 3
    stock_val = stock[grading_metric]

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

st.markdown("---")
st.caption("Built with Streamlit | Data Source: Finviz.com")
# --- Grading System ---
st.markdown("---")
st.header("📘 Grading System")

st.markdown("""
The grading system compares a stock’s metric within its **sector or industry** and calculates:

- 📊 **Mean** of that metric in the group  
- 🏁 **90th Percentile**  
- 📉 **Change** = (Standard Deviation / 3)  
- 🔴 Red line shows your stock’s value
""")

grading_metric = st.selectbox("📐 Select Grading Metric", available_metrics, key="grading")
grading_scope = st.radio("📊 Grading Scope", ["Sector", "Industry"], horizontal=True)

if ticker in df['Ticker'].values and grading_metric in df.columns:
    group = stock[grading_scope]
    grading_df = df[df[grading_scope] == group]

    values = grading_df[grading_metric].dropna()
    mean_val = values.mean()
    p90_val = values.quantile(0.9)
    std_val = values.std()
    change_val = std_val / 3
    stock_val = stock[grading_metric]

    st.markdown(f"""
    ```
    {group} {grading_metric} Avg: {mean_val:.2f}
    90th Percentile: {p90_val:.3f}
    Change: {change_val:.4f}
    ```
    """)

    fig, ax = plt.subplots()
    sns.histplot(values, kde=True, bins=25, ax=ax, color='skyblue')
    ax.axvline(mean_val, color='blue', linestyle='--', label='Mean')
    ax.axvline(p90_val, color='green', linestyle='--', label='90th Percentile')
    ax.axvline(stock_val, color='red', linestyle='-', label=ticker)
    ax.set_title(f"{grading_metric} Distribution in {group} {grading_scope}")
    ax.legend()
    st.pyplot(fig)

