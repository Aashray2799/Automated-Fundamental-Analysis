

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit config
st.set_page_config(page_title="Automated Fundamental Analysis", layout="wide")

# Title & Intro
st.title("📊 Automated Fundamental Analysis")

st.markdown("""
This program rates **8,300+ stocks** based on numerical metrics like valuation, profitability, growth, and price performance, all relative to their **sector**.

Data source: Finviz.com  
Example dataset: `StockRatings-04.05.22.csv`
""")

# Load dataset
try:
    df = pd.read_csv("StockRatings-04.05.22.csv")
except Exception as e:
    st.error(f"❌ Could not load dataset.\n\nError: {e}")
    st.stop()

# Sidebar column preview
st.sidebar.subheader("📋 Columns in Dataset")
st.sidebar.write(df.columns.tolist())

# Identify usable metrics
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
excluded = ["Price", "Market Cap"]
metric_cols = [col for col in numeric_cols if col not in excluded]

if not metric_cols:
    st.error("❌ No usable numeric columns found in the dataset for analysis.")
    st.stop()

st.markdown("---")

# --- Ticker Section ---
ticker = st.text_input("Enter a stock ticker", value="AAPL").upper()

if ticker in df['Ticker'].values:
    stock = df[df['Ticker'] == ticker].iloc[0]

    st.subheader(f"{stock['Company']} ({stock['Ticker']})")

    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${stock['Price']}")
    col2.metric("Market Cap", f"{stock['Market Cap']}B")
    col3.metric("Overall Rating", stock.get("Overall Rating", "N/A"))

    col4, col5 = st.columns(2)
    col4.metric("Sector", stock['Sector'])
    col5.metric("Industry", stock['Industry'])

    st.markdown("### 🔍 Analyze Metric Within Sector or Industry")
    selected_metric = st.selectbox("Select Metric", metric_cols)
    scope = st.radio("Compare within:", ["Sector", "Industry"])
    group = stock[scope]
    scoped_df = df[df[scope] == group]

    st.markdown(f"**{ticker} {selected_metric}: {stock[selected_metric]}**")
    fig, ax = plt.subplots()
    sns.histplot(scoped_df[selected_metric], kde=True, ax=ax)
    ax.axvline(stock[selected_metric], color='red', linestyle='--', label='Selected Stock')
    ax.set_title(f"{selected_metric} Distribution in {group} {scope}")
    ax.legend()
    st.pyplot(fig)

else:
    st.warning("Enter a valid ticker from the dataset.")

# --- Sector Comparison ---
st.markdown("---")
st.header("📊 Compare Metrics Between Sectors")

sectors = sorted(df['Sector'].dropna().unique())
sector1 = st.selectbox("Select Sector 1", sectors)
sector2 = st.selectbox("Select Sector 2", sectors, index=1 if sectors[0] == sector1 else 0)
compare_metric = st.selectbox("Metric to Compare", metric_cols)

df1 = df[df['Sector'] == sector1]
df2 = df[df['Sector'] == sector2]

fig2, ax2 = plt.subplots()
sns.kdeplot(df1[compare_metric], fill=True, alpha=0.5, label=sector1)
sns.kdeplot(df2[compare_metric], fill=True, alpha=0.5, label=sector2)
ax2.set_title(f"{compare_metric} Distribution: {sector1} vs {sector2}")
ax2.legend()
st.pyplot(fig2)

# --- Grading System ---
st.markdown("---")
st.header("📘 Grading System")

st.markdown("""
Grading is based on how a stock's metric compares to others in its sector or industry:

- 📊 **Mean**
- 🏁 **90th Percentile**
- 🔁 **Change** = Std. Dev ÷ 3
""")

grading_metric = st.selectbox("Grading Metric", metric_cols, key="grading_metric")
grading_scope = st.radio("Grading Scope", ["Sector", "Industry"], horizontal=True)

if ticker in df['Ticker'].values:
    grading_group = stock[grading_scope]
    grading_df = df[df[grading_scope] == grading_group]

    if grading_metric in grading_df.columns:
        values = grading_df[grading_metric].dropna()
        mean_val = values.mean()
        p90_val = values.quantile(0.9)
        std_val = values.std()
        change_val = std_val / 3
        stock_val = stock[grading_metric]

        st.markdown(f"""
        ```
        {grading_group} {_



