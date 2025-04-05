import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ Confirmation message
st.info("✅ Running the clean morning version of the app")

# Page config
st.set_page_config(page_title="Automated Fundamental Analysis", layout="centered")
st.title("📊 Automated Fundamental Analysis")

st.markdown("""
This app rates stocks out of 100 based on **valuation, profitability, growth, and performance**, relative to sector.

📁 Dataset: `StockRatings-04.05.22.csv`
""")

# Load Data
try:
    df = pd.read_csv("StockRatings-04.05.22.csv")
except Exception as e:
    st.error(f"Could not load CSV: {e}")
    st.stop()

# Grade conversion map
grade_map = {
    'A+': 10, 'A': 9, 'A-': 8,
    'B+': 7, 'B': 6, 'B-': 5,
    'C+': 4, 'C': 3, 'C-': 2,
    'D+': 1, 'D': 0, 'D-': -1, 'F': -2
}

# Ticker analysis
st.header("🔍 Stock Lookup")
ticker = st.text_input("Enter a stock ticker", "AAPL").upper()

if ticker in df['Ticker'].values:
    stock = df[df['Ticker'] == ticker].iloc[0]
    st.subheader(f"{stock['Company']} ({ticker})")

    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${stock['Price']}")
    col2.metric("Market Cap", stock['Market Cap'])
    col3.metric("Overall Rating", stock['Overall Rating'])

    col4, col5 = st.columns(2)
    col4.metric("Sector", stock['Sector'])
    col5.metric("Industry", stock['Industry'])

    metric_options = [
        'Overall Rating',
        'Valuation Grade',
        'Profitability Grade',
        'Growth Grade',
        'Performance Grade'
    ]
    available_metrics = [m for m in metric_options if m in df.columns]

    st.markdown("### 📈 Metric Distribution")
    selected_metric = st.selectbox("Select a metric", available_metrics)
    scope = st.radio("Analyze within", ["Sector", "Industry"])
    group = stock[scope]
    scoped_df = df[df[scope] == group]

    if scoped_df[selected_metric].dtype == 'object':
        scoped_df[selected_metric] = scoped_df[selected_metric].map(grade_map)
        selected_val = grade_map.get(stock[selected_metric], None)
    else:
        scoped_df[selected_metric] = pd.to_numeric(scoped_df[selected_metric], errors="coerce")
        selected_val = stock[selected_metric]

    fig, ax = plt.subplots()
    sns.histplot(scoped_df[selected_metric].dropna(), kde=True, ax=ax)
    ax.axvline(selected_val, color='red', linestyle='--', label=ticker)
    ax.set_title(f"{selected_metric} in {group} {scope}")
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("⚠️ Ticker not found.")

# Sector Comparison
st.markdown("---")
st.header("🏆 Sector Comparison")

sectors = sorted(df['Sector'].dropna().unique())
sector1 = st.selectbox("Sector 1", sectors)
sector2 = st.selectbox("Sector 2", sectors, index=1 if sector1 == sectors[0] else 0)
compare_metric = st.selectbox("Metric to compare", available_metrics, key="compare")

def convert_metric(series):
    return series.map(grade_map) if series.dtype == 'object' else pd.to_numeric(series, errors='coerce')

df1 = df[df['Sector'] == sector1].copy()
df2 = df[df['Sector'] == sector2].copy()
df1[compare_metric] = convert_metric(df1[compare_metric])
df2[compare_metric] = convert_metric(df2[compare_metric])

fig2, ax2 = plt.subplots()
sns.kdeplot(df1[compare_metric].dropna(), fill=True, label=sector1, alpha=0.5)
sns.kdeplot(df2[compare_metric].dropna(), fill=True, label=sector2, alpha=0.5)
ax2.set_title(f"{compare_metric}: {sector1} vs {sector2}")
ax2.legend()
st.pyplot(fig2)

# Grading System
st.markdown("---")
st.header("📘 Grading System")

grading_metric = st.selectbox("Grading metric", available_metrics, key="grading")
grading_scope = st.radio("Grade within", ["Sector", "Industry"], horizontal=True)
group = stock[grading_scope]
grading_df = df[df[grading_scope] == group].copy()

if grading_df[grading_metric].dtype == 'object':
    grading_df[grading_metric] = grading_df[grading_metric].map(grade_map)
    stock_val = grade_map.get(stock[grading_metric], None)
else:
    grading_df[grading_metric] = pd.to_numeric(grading_df[grading_metric], errors="coerce")
    stock_val = stock[grading_metric]

values = grading_df[grading_metric].dropna()

if stock_val is not None and not values.empty:
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
    st.warning("⚠️ No grading data available.")

# Footer
st.markdown("---")
st.caption("Built with Streamlit · Data from Finviz.com")




