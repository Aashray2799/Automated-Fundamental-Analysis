import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fundamental Analysis Web App", layout="wide")

st.title("📊 Automated Fundamental Analysis")
st.write("Enter a stock ticker below to get the latest fundamentals.")

ticker = st.text_input("Stock Ticker", value="AAPL").upper()

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        st.subheader(f"Company Overview: {info.get('shortName', 'N/A')}")
        st.write(info.get("longBusinessSummary", "No summary available."))

        col1, col2, col3 = st.columns(3)
        col1.metric("Market Cap", f"${info.get('marketCap', 0):,.0f}")
        col2.metric("PE Ratio (TTM)", info.get("trailingPE", 'N/A'))
        col3.metric("EPS (TTM)", info.get("trailingEps", 'N/A'))

        col4, col5, col6 = st.columns(3)
        col4.metric("ROE", f"{info.get('returnOnEquity', 0) * 100:.2f}%")
        col5.metric("Profit Margin", f"{info.get('profitMargins', 0) * 100:.2f}%")
        col6.metric("Debt to Equity", info.get("debtToEquity", 'N/A'))

        st.subheader("📈 Historical Revenue & Net Income")

        financials = stock.financials.T
        if not financials.empty and 'Total Revenue' in financials.columns and 'Net Income' in financials.columns:
            income = financials[['Total Revenue', 'Net Income']].dropna()

            st.dataframe(income)

            fig, ax = plt.subplots()
            income.plot(kind='bar', ax=ax)
            ax.set_ylabel('Amount ($)')
            ax.set_title('Revenue vs Net Income')
            st.pyplot(fig)
        else:
            st.warning("Financial data not available for this stock.")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
