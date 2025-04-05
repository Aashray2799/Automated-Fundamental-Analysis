import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Set page config ---
st.set_page_config(page_title="Automated Fundamental Analysis", layout="centered")

# --- Load Data ---
try:
    df = pd.read_csv("StockRatings-04.05.22.csv")
except Exception as e:
    st.error(f"❌ Failed to load CSV. Error: {e}")
    st.stop()

# --- Column Definitions ---
required_cols = ['Ticker', 'Company', 'Price', 'Market Cap', 'Sector', 'Industry', 'Overall Rating']
metric_cols = ['Overall Rating', 'Valuation Grade', 'Profitability Grade', 'Growth Grade', 'Performance Grade']
metric_cols = [m for m in metric_cols if m in df.columns]

# --- Sidebar for debug ---
st.sidebar.header("📋 Columns in Dataset")
st.sidebar.write(df.columns.tolist())

# --- Title ---
st.title("📊 Automated Fundamental Analysis")

st.markdown("""
This program analyzes **8,000+ stocks** based on valuation, profitability, growth, and performance—
relative to their **sector or industry**.

📁 Dataset: `StockRatings-04.05.22.csv`
""")

st.markdown("___")

# --- Ticker Input ---
ticker = st.text_input("🔎 Enter a Stock Ticker", value="AAPL").upper()

if ticker in df['Ticker'].values:
    stock = df[df['Ticker'] == ticker].iloc[0]

    st.subheader(f"{stock['Company']} ({ticker})")

    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Price", f"${stock['Price']}")
        col2.metric("Market Cap", f"{stock['Market Cap']}B")
        col3.metric("Overall Rating", stock['Overall Rating'])

    col4, col5 = st.columns(2)
    col4.metric("Sector", stock['Sector'])
    col5.metric("Industry", stock['Industry'])

    st.markdown("___")

    # --- Metric Analysis ---
    st.header("📈 Metric Distribution")
    selected_metric = st.selectbox("Choose a Metric", metric_cols)
    scope = st.radio("Compare Within", ["Sector", "Industry"])
    group = stock[scope]
    scoped_df = df[df[scope] == group]

    fig, ax = plt.subplots()
    sns.histplot(scoped_df[selected_metric], kde=True, ax=ax)
    ax.axvline(stock[selected_metric], color='red', linestyle='--', label='Selected Stock')
    ax.set_title(f"{selected_metric} Distribution in {group} {scope}")
    ax.legend()
    st.pyplot(fig)

else:
    st.warning("⚠️



