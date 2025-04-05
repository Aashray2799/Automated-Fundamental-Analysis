import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Automated Fundamental Analysis", layout="wide")

# Title
st.title("📊 Automated Fundamental Analysis")

# Intro
st.markdown("""
This Python program rates **8,300+ stocks** out of 100 based on:

- 📉 **Valuation**
- 💰 **Profitability**
- 🚀 **Growth**
- 📈 **Price Performance**

Ratings are calculated **relative to their sector** using Finviz.com data.
""")

# Load Data
try:
    df = pd.read_csv("StockRatings-04.05.22.csv")
except Exception as e:
    st.error(f"❌ Could not load StockRatings-04.05.22.csv\n\nError: {e}")
    st.stop()

st.markdown("---")

# Ticker input
ticker = st.text_input("Enter a Ticker Symbol", value="AAPL").upper()

if ticker in df['Ticker'].values:
    stock = df[df['Ticker'] == ticker].iloc[0]

    # Company Info
    st.subheader(f"{stock['Company']} ({stock['Ticker']})")

    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${stock['Price']}")
    col2.metric("Market Cap", f"{stock['Market Cap']}B")
    col3.metric("Overall Rating", stock['Overall Rating'])

    col4, col5 = st.columns(2)
    col4.metric("Sector", stock['Sector'])
    col5.metric("Industry", stock['Industry'])

    st.markdown("### Pick a metric to analyze")
    metric = st.selectbox("Metric", ["Overall Rating", "Valuation", "Profitability", "Growth", "Performance"])

    st.markdown("### Analyze by")
    analysis_scope = st.radio("Choose comparison scope:", ["Sector", "Industry"])
    scope_value = stock[analysis_scope]
    scoped_df = df[df[analysis_scope] == scope_value]

    st.markdown(f"### {ticker} {metric}: {stock[metric]}")
    st.markdown(f"Distribution of {metric} values in the {scope_value} {analysis_scope}")

    fig, ax = plt.subplots()
    sns.histplot(scoped_df[metric], kde=True, ax=ax)
    ax.axvline(stock[metric], color='red', linestyle='--', label='Selected Stock')
    ax.legend()
    st.pyplot(fig)

else:
    st.info("Enter a valid ticker from the dataset to see results.")

# Sector vs. Sector comparison
st.markdown("---")
st.header("Select two Sectors and compare a metric")

sectors = sorted(df['Sector'].dropna().unique())
sector1 = st.selectbox("Select a Sector", sectors, key="sector1")
sector2 = st.selectbox("Select a Sector to Compare", sectors, index=1 if sectors[0] == sector1 else 0, key="sector2")
compare_metric = st.selectbox("Select a Metric", ["Overall Rating", "Valuation", "Profitability", "Growth", "Performance"])

df1 = df[df['Sector'] == sector1]
df2 = df[df['Sector'] == sector2]

fig2, ax2 = plt.subplots()
sns.kdeplot(df1[compare_metric], fill=True, label=sector1, alpha=0.5)
sns.kdeplot(df2[compare_metric], fill=True, label=sector2, alpha=0.5)
ax2.set_title(f"{compare_metric} Comparison: {sector1} vs {sector2}")
ax2.legend()
st.pyplot(fig2)

st.markdown("---")
st.caption("📈 Built with Python, Streamlit, and data from Finviz.com")
# --- Grading System Section ---
st.markdown("---")
st.header("📘 Grading System")

st.markdown("""
The grading system used in this program is based on the normal distribution of values for a certain metric within a sector or industry.

For example, if we want to grade the **Net Margin** of a stock in the **Technology** sector, we look at the net margins of all the stocks in that sector and compare our stock's value to this distribution.

We calculate:
- 📊 **Average (Mean)** of the metric
- 🏁 **90th Percentile** (top performers)
- 🔁 **Change value** = Standard deviation ÷ 3

This allows us to understand where a stock sits relative to its peers.
""")

# --- Metric Grading Breakdown ---
grading_metric = st.selectbox("Select Metric for Grading Visual", ["Valuation", "Profitability", "Growth", "Performance", "Overall Rating"])
grading_scope = st.radio("Grade within:", ["Sector", "Industry"], horizontal=True)

if ticker in df['Ticker'].values:
    group_value = stock[grading_scope]
    scoped_df = df[df[grading_scope] == group_value]
    values = scoped_df[grading_metric].dropna()

    # Grading stats
    mean_val = values.mean()
    p90_val = values.quantile(0.9)
    std_dev = values.std()
    change_val = std_dev / 3
    stock_val = stock[grading_metric]

    # Grading display like README
    st.markdown(f"""
    **{group_value} {grading_metric} Stats:**  
    - Average: `{mean_val:.2f}`  
    - 90th Percentile: `{p90_val:.3f}`  
    - Change: `{change_val:.4f}`  
    - Stock’s {grading_metric}: `{stock_val:.2f}`
    """)

    # Plot
    fig, ax = plt.subplots()
    sns.histplot(values, kde=True, bins=25, ax=ax)
    ax.axvline(mean_val, color='blue', linestyle='--', label='Mean')
    ax.axvline(p90_val, color='green', linestyle='--', label='90th Percentile')
    ax.axvline(stock_val, color='red', linestyle='-', label=f"{ticker}")
    ax.set_title(f"{grading_metric} Distribution in {group_value} {grading_scope}")
    ax.legend()
    st.pyplot(fig)
else:
    st.info("Enter a valid ticker to view grading visuals.")



