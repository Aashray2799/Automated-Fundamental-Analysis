import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Automated Fundamental Analysis", layout="wide")

# Title and Intro
st.title("📊 Automated Fundamental Analysis")

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
st.header("🏆 Compare Metrics Between Sectors")

sectors = sorted(df['Sector'].dropna().unique())
sector1 = st.selectbox("Select a Sector", sectors, key="sector1")
sector2 = st.selectbox("Select a Sector to Compare", sectors, index=1 if sectors[0] == sector1 else 0, key="sector2")
compare_metric = st.selectbox("Select a Metric", ["Overall Rating", "Valuation", "Profitability", "Growth", "Performance"])

df1 = df[df['Sector'] == sector1]
df2 = df[df['Sector'] == sector2]

fig2, ax2 = plt.subplots()
sns.kdeplot(df1[compare_metric], fill=True, label=sector1, alpha=0.5)
sns.kdeplot(df2[compare_metric], fill=True, label=sector2, alpha=0.5)
ax2.set_title(f"{compare_metric} Distribution: {sector1} vs {sector2}")
ax2.legend()
st.pyplot(fig2)

# Grading system
st.markdown("---")
st.header("📘 Grading System")

st.markdown("""
The grading system used in this program is based on the normal distribution of values for a certain metric within a sector.

For example, to grade the **Net Margin** of a stock in the Technology sector, we look at the net margins of all stocks in that sector and determine where this stock lies in the distribution.

We calculate:
- 📊 **Average (Mean)**
- 🏁 **90th Percentile**
- 🔁 **Change** = (Standard Deviation ÷ 3)

This helps assign a rating based on relative performance — just like a report card.
""")

grading_metric = st.selectbox("Select Metric for Grading Breakdown", ["Valuation", "Profitability", "Growth", "Performance", "Overall Rating"])
grading_scope = st.radio("Compare within:", ["Sector", "Industry"], horizontal=True)

if ticker in df['Ticker'].values:
    group_val = stock[grading_scope]
    df_scope = df[df[grading_scope] == group_val]
    values = df_scope[grading_metric].dropna()

    # Compute grading numbers
    mean_val = values.mean()
    p90_val = values.quantile(0.9)
    std_val = values.std()
    change_val = std_val / 3
    stock_val = stock[grading_metric]

    # Display values like your README screenshot
    st.markdown(f"""
    ```
    {group_val} {grading_metric} Avg: {mean_val:.2f}
    90th Percentile: {p90_val:.3f}
    Change: {change_val:.4f}
    ```
    """)

    # Plot
    fig3, ax3 = plt.subplots()
    sns.histplot(values, kde=True, bins=25, ax=ax3, color='skyblue')
    ax3.axvline(mean_val, color='blue', linestyle='--', label='Mean')
    ax3.axvline(p90_val, color='green', linestyle='--', label='90th Percentile')
    ax3.axvline(stock_val, color='red', linestyle='-', label=f'{ticker}')
    ax3.set_title(f"{grading_metric} Distribution in {group_val} {grading_scope}")
    ax3.legend()
    st.pyplot(fig3)

st.markdown("---")
st.caption("📈 Built with Python, Streamlit, and data from Finviz.com")





