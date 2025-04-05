import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Automated Fundamental Analysis", layout="centered")
st.title("📊 Automated Fundamental Analysis")

st.markdown("""
Analyze **8,000+ stocks** based on valuation, profitability, growth, and performance grades — **relative to their sector or industry**.

📁 Data: `StockRatings-04.05.22.csv`
""")

# Load dataset
try:
    df = pd.read_csv("StockRatings-04.05.22.csv")
except Exception as e:
    st.error(f"❌ Could not load StockRatings-04.05.22.csv\n\n{e}")
    st.stop()

# Grade conversion
grade_map = {
    'A+': 10, 'A': 9, 'A-': 8,
    'B+': 7, 'B':

