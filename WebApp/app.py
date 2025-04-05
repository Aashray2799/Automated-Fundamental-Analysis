import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Set wide layout ---
st.set_page_config(page_title="Automated Fundamental Analysis", layout="wide")

# --- App Title ---
st.title("📊 Automated Fundamental Analysis")

# --- Intro Description ---
st.markdown("""
Welcome to the **Automated Fundamental Analysis** web app!

This Python program rates **8,300+ stocks** out of 100 based on:

- 📉 **Valuation**
- 💰 **Profitability**
- 🚀 **Growth**
- 📈 **Price Performance**

Ratings are calculated **relative to their sector** using data scraped from **Finviz.com**.

📁 The file `StockRatings-04.05.22.csv` is the output of this analysis engine.
""")

st.markdown("---")

# --- Load CSV file ---
try:
    df = pd.read_csv("StockRatings-04.05.22.csv")
except Exception as e:
    st.error(f"❌ Could not load StockRatings-04.05.22.csv.\n\nError: {e}")
    st.stop()

# --- Ticker Input ---
ticker_input = st.text_input("🔎 Enter a Stock Ticker Symbol", value="AAPL").upper()

if ticker_input in df['Ticker'].values:
    stock = df[df['Ticker'] == ticker_input].iloc[0]

    st.header(f"📌 {stock['Company']} ({stock['Ticker']})")

    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${stock['Price']}")
    col2.metric("Market Cap", f"{stock['Market Cap']}B")
    col3.metric("Overall Rating", stock['Overall Rating'])

    col4, col5 = st.columns(2)
    col4.metric("Sector", stock['Sector'])
    col5.metric("Industry", stock['Industry'])

    st.markdown("---")

    # --- Metric Analysis ---
    st.subheader("📊 Analyze Metrics Within Sector or Industry")
    metric = st.selectbox("Select a Metric", ["Overall Rating", "Valuation", "Profitability", "Growth", "Performance"])
    scope = st.radio("Compare within:", ["Sector", "Industry"])
    filter_col = stock[scope]
    filtered_df = df[df[scope] == filter_col]

    st.markdown(f"### {ticker_input} {metric}: **{stock[metric]}**")
    st.markdown(f"Distribution of **{metric}** in the **{filter_col} {scope}**")

    fig1, ax1 = plt.subplots()
    sns.histplot(filtered_df[metric], kde=True, bins=20, ax=ax1)
    ax1.axvline(stock[metric], color='red', linestyle='--', label='Selected Stock')
    ax1.legend()
    st.pyplot(fig1)

else:
    st.warning("⚠️ Ticker not found in dataset. Please try another one.")

# --- Sector Comparison ---
st.markdown("---")
st.header("🏆 Compare Metrics Between Sectors")

sectors = sorted(df['Sector'].dropna().unique())
sector1 = st.selectbox("Select First Sector", sectors)
sector2 = st.selectbox("Select Second Sector", sectors, index=1 if sectors[0] == sector1 else 0)
compare_metric = st.selectbox("Metric to Compare", ["Overall Rating", "Valuation", "Profitability", "Growth", "Performance"])

df1 = df[df['Sector'] == sector1]
df2 = df[df['Sector'] == sector2]

fig2, ax2 = plt.subplots()
sns.kdeplot(df1[compare_metric], label=sector1, fill=True, alpha=0.5)
sns.kdeplot(df2[compare_metric], label=sector2, fill=True, alpha=0.5)
ax2.set_title(f"{compare_metric} Distribution: {sector1} vs {sector2}")
ax2.legend()
st.pyplot(fig2)

st.markdown("---")
st.caption("Built with ❤️ using Python and Streamlit | Data Source: Finviz.com")

