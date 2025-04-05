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


