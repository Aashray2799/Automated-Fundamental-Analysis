import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(page_title="Automated Fundamental Analysis", layout="wide")

# Title and Introduction
st.title("📊 Automated Fundamental Analysis")

st.markdown("""
This application analyzes stocks based on various financial metrics relative to their sector or industry.
""")

# Load Data
try:
    df = pd.read_csv("StockRatings-04.05.22.csv")
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# Display available columns in the sidebar for reference
st.sidebar.subheader("📋 Available Columns in Dataset")
st.sidebar.write(df.columns.tolist())

# Identify numeric columns for metric analysis
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
excluded_cols = ['Ticker', 'Company', 'Sector', 'Industry', 'Price', 'Market Cap']
metric_columns = [col for col in numeric_cols if col not in excluded_cols]

if not metric_columns:
    st.error("❌ No suitable numeric columns found for



