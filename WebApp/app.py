import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load ratings CSV
df = pd.read_csv("StockRatings-04.05.22.csv")

st.set_page_config(page_title="Automated Fundamental Analysis", layout="wide")

st.title("📊 Automated Fundamental Analysis Web App")

# --- Stock Ticker Input ---
ticker_input = st.text_input("Enter a Ticker Symbol", value="AAPL").upper()

if ticker_input in df['Ticker'].values:
    stock = df[df['Ticker'] == ticker_input].iloc[0]
    
    st.subheader(f"{stock['Company']} ({stock['Ticker']})")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${stock['Price']}")
    col2.metric("Market Cap", f"{stock['Market Cap']}B")
    col3.metric("Overall Rating", stock['Overall Rating'])

    col4, col5 = st.columns(2)
    col4.metric("Sector", stock['Sector'])
    col5.metric("Industry", stock['Industry'])
    
    # --- Metric Selection ---
    st.markdown("### Pick a metric to analyze")
    metric = st.selectbox("Metric", ["Overall Rating", "Valuation", "Profitability", "Growth", "Performance"])

    # --- Sector or Industry Analysis ---
    analysis_type = st.radio("Analyze by", ["Sector", "Industry"])
    filter_column = stock[analysis_type]
    filtered_df = df[df[analysis_type] == filter_column]

    st.markdown(f"### {ticker_input} {metric}: {stock[metric]}")
    st.markdown(f"Distribution of {metric} in the {filter_column} {analysis_type}")

    fig, ax = plt.subplots()
    sns.histplot(filtered_df[metric], kde=True, bins=20, ax=ax)
    ax.axvline(stock[metric], color='red', linestyle='--', label='This Stock')
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("Ticker not found in the dataset.")

# --- Sector Comparison ---
st.markdown("---")
st.header("📊 Compare Sectors")

sectors = df['Sector'].unique().tolist()
sector1 = st.selectbox("Select a Sector", sectors)
sector2 = st.selectbox("Select a Sector to Compare", sectors, index=1 if sectors[0] == sector1 else 0)
compare_metric = st.selectbox("Select a Metric", ["Overall Rating", "Valuation", "Profitability", "Growth", "Performance"])

df1 = df[df['Sector'] == sector1]
df2 = df[df['Sector'] == sector2]

fig2, ax2 = plt.subplots()
sns.kdeplot(df1[compare_metric], label=sector1, fill=True)
sns.kdeplot(df2[compare_metric], label=sector2, fill=True)
ax2.set_title(f"{compare_metric} Comparison: {sector1} vs {sector2}")
ax2.legend()
st.pyplot(fig2)
