import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit layout
st.set_page_config(page_title="Automated Fundamental Analysis", layout="wide")

# App Title
st.title("📊 Automated Fundamental Analysis")

# Introduction
st.markdown("""
This program analyzes **8,300+ stocks** based on financial metrics (like valuation, profitability, and growth), 
compared to their sector or industry peers.

📁 Dataset used: `StockRatings-04.05.22.csv`  
📊 Source: Finviz.com
""")

# Load Dataset
try:
    df = pd.read_csv("StockRatings-04.05.22.csv")
except Exception as e:
    st.error(f"❌ Failed to load CSV. Error: {e}")
    st.stop()

# Sidebar: show actual column names for debugging
st.sidebar.header("📋 Dataset Columns")
st.sidebar.write(df.columns.tolist())

# Extract numeric columns, excluding irrelevant ones
excluded_columns = ['Price', 'Market Cap']
numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
metric_columns = [col for col in numeric_columns if col not in excluded_columns]

if not metric_columns:
    st.error("❌ No suitable numeric columns found for analysis.")
    st.stop()

# --- Ticker Search Section ---
ticker = st.text_input("Enter a Stock Ticker", value="AAPL").upper()

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

    st.markdown("### 🔍 Analyze a Metric")
    selected_metric = st.selectbox("Select a Metric", metric_columns)
    scope = st.radio("Compare within:", ["Sector", "Industry"])
    group_val = stock[scope]
    scoped_df = df[df[scope] == group_val]

    if selected_metric in scoped_df.columns:
        st.markdown(f"**{ticker}'s {selected_metric}: {stock[selected_metric]}**")
        fig, ax = plt.subplots()
        sns.histplot(scoped_df[selected_metric], kde=True, ax=ax)
        ax.axvline(stock[selected_metric], color='red', linestyle='--', label=ticker)
        ax.set_title(f"{selected_metric} Distribution in {group_val} {scope}")
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning(f"⚠️ '{selected_metric}' not found in selected group data.")

else:
    st.warning("⚠️ Ticker not found. Please enter a valid stock symbol from the dataset.")

# --- Sector Comparison ---
st.markdown("---")
st.header("🏆 Compare Metrics Between Sectors")

sectors = sorted(df['Sector'].dropna().unique())
sector1 = st.selectbox("Sector 1", sectors)
sector2 = st.selectbox("Sector 2", sectors, index=1 if sectors[0] == sector1 else 0)
compare_metric = st.selectbox("Metric to Compare", metric_columns, key="sector_compare_metric")

df1 = df[df['Sector'] == sector1]
df2 = df[df['Sector'] == sector2]

fig2, ax2 = plt.subplots()
sns.kdeplot(df1[compare_metric], fill=True, label=sector1, alpha=0.5)
sns.kdeplot(df2[compare_metric], fill=True, label=sector2, alpha=0.5)
ax2.set_title(f"{compare_metric} Distribution: {sector1} vs {sector2}")
ax2.legend()
st.pyplot(fig2)

# --- Grading System ---
st.markdown("---")
st.header("📘 Grading System Breakdown")

st.markdown("""
To grade a stock, we compare its metric against all others in the same **Sector or Industry**.

We calculate:
- 📊 **Mean** of the group
- 🏁 **90th Percentile**
- 🔁 **Change** = (Standard Deviation ÷ 3)
""")

grading_metric = st.selectbox("Grading Metric", metric_columns, key="grading_metric")
grading_scope = st.radio("Grade within:", ["Sector", "Industry"], horizontal=True)

if ticker in df['Ticker'].values:
    group = stock[grading_scope]
    grading_df = df[df[grading_scope] == group]

    if grading_metric in grading_df.columns:
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
        ax3.set_title(f"{grading_metric} in {group} {grading_scope}")
        ax3.legend()
        st.pyplot(fig3)

st.markdown("---")
st.caption("📈 Built with Python & Streamlit | Data: Finviz.com")


