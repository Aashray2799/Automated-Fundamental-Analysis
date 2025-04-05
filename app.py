# --- Grading System ---
st.markdown("---")
st.header("📘 Grading System")

st.markdown("""
The grading system compares a stock’s metric within its **sector or industry** and calculates:

- 📊 **Mean** of that metric in the group  
- 🏁 **90th Percentile**  
- 📉 **Change** = (Standard Deviation / 3)  
- 🔴 Red line shows your stock’s value
""")

grading_metric = st.selectbox("📐 Select Grading Metric", available_metrics, key="grading")
grading_scope = st.radio("📊 Grading Scope", ["Sector", "Industry"], horizontal=True)

if ticker in df['Ticker'].values and grading_metric in df.columns:
    group = stock[grading_scope]
    grading_df = df[df[grading_scope] == group]

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

    fig, ax = plt.subplots()
    sns.histplot(values, kde=True, bins=25, ax=ax, color='skyblue')
    ax.axvline(mean_val, color='blue', linestyle='--', label='Mean')
    ax.axvline(p90_val, color='green', linestyle='--', label='90th Percentile')
    ax.axvline(stock_val, color='red', linestyle='-', label=ticker)
    ax.set_title(f"{grading_metric} Distribution in {group} {grading_scope}")
    ax.legend()
    st.pyplot(fig)

