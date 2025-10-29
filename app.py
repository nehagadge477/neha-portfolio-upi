# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="UPI Transaction Analysis — Neha Gadge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Custom CSS for white-blue modern look
# ---------------------------
page_bg = """
<style>
.reportview-container .main .block-container{
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
h1, h2, h3 { font-family: "Inter", sans-serif; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
    border-right: 1px solid rgba(0,0,0,0.04);
}
.stMetric > div:nth-child(1) { color: #0b5394; font-weight: 600; }
.stButton>button { background-color:#0b66c2; color: white; border-radius: 10px; }
tbody th, tbody td { border-bottom: 1px solid rgba(11,102,194,0.06); }
.small { font-size:12px; color: #666; }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------------------------
# Title & subtitle
# ---------------------------
st.title("UPI Transaction Analysis Dashboard — Neha Gadge")
st.markdown(
    """
*Interactive dashboard* showing trends, top merchants, payment methods, and transaction insights.
- Modern white & blue theme  
- Upload your UPI+Transactions.xlsx or place it under data/UPI+Transactions.xlsx in repo
"""
)

# ---------------------------
# Data loader (uploaded or default)
# ---------------------------
@st.cache_data
def load_from_path(path="filtered_upi_transactions.csv"):
    try:
        df = pd.read_csv(path, engine="openpyxl")
        return df
    except Exception:
        return None

@st.cache_data
def load_from_file(uploaded_file):
    if uploaded_file is None:
        return None
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".xlsx") or name.endswith(".xls"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            df = pd.read_csv(uploaded_file)
        return df
    except Exception:
        uploaded_file.seek(0)
        try:
            df = pd.read_csv(uploaded_file)
            return df
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
            return None

st.sidebar.header("Data ▶ Upload / Filters")
uploaded = st.sidebar.file_uploader("Upload Excel (.xlsx) or CSV (optional)", type=["xlsx", "csv"])

if uploaded:
    df = load_from_file(uploaded)
else:
    df = load_from_path()

if df is None:
    st.info("No data found. Upload your UPI+Transactions.xlsx or add it in /data/ folder of the repo.")
    st.stop()

# ---------------------------
# Standardize column names (strip)
# ---------------------------
df.columns = df.columns.str.strip()

# Parse dates and times
if "TransactionDate" in df.columns:
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], errors="coerce")
    df["YearMonth"] = df["TransactionDate"].dt.to_period("M").astype(str)
    df["DateOnly"] = df["TransactionDate"].dt.date
else:
    df["YearMonth"] = np.nan

if "TransactionTime" in df.columns:
    try:
        df["TransactionTime_parsed"] = pd.to_datetime(df["TransactionTime"].astype(str), errors="coerce").dt.time
        df["Hour"] = pd.to_datetime(df["TransactionTime"].astype(str), errors="coerce").dt.hour
    except Exception:
        df["Hour"] = np.nan
else:
    df["Hour"] = np.nan

if "Amount" in df.columns:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

# ---------------------------
# Sidebar filters (auto-populate)
# ---------------------------
st.sidebar.subheader("Filters")
# Date range
if "TransactionDate" in df.columns:
    min_d = df["TransactionDate"].min().date()
    max_d = df["TransactionDate"].max().date()
    date_range = st.sidebar.date_input("Date range", [min_d, max_d])
else:
    date_range = None

# City filter
if "City" in df.columns:
    cities = sorted(df["City"].dropna().unique().tolist())
    selected_cities = st.sidebar.multiselect("City", options=cities, default=cities[:5])
else:
    selected_cities = []

# Payment method
if "PaymentMethod" in df.columns:
    pms = df["PaymentMethod"].dropna().unique().tolist()
    selected_pms = st.sidebar.multiselect("Payment Method", options=sorted(pms), default=sorted(pms))
else:
    selected_pms = []

# Status
if "Status" in df.columns:
    statuses = df["Status"].dropna().unique().tolist()
    selected_status = st.sidebar.multiselect("Status", options=statuses, default=statuses)
else:
    selected_status = []

# Amount slider
if "Amount" in df.columns:
    a_min = float(df["Amount"].min(skipna=True))
    a_max = float(df["Amount"].max(skipna=True))
    selected_amount = st.sidebar.slider("Amount range", a_min, a_max, (a_min, min(a_min + (a_max - a_min) * 0.1, a_max)))
else:
    selected_amount = None

# Apply filters
df_f = df.copy()
if date_range and "TransactionDate" in df_f.columns and len(date_range) == 2:
    df_f = df_f[(df_f["TransactionDate"].dt.date >= date_range[0]) & (df_f["TransactionDate"].dt.date <= date_range[1])]
if selected_cities:
    df_f = df_f[df_f["City"].isin(selected_cities)]
if selected_pms:
    df_f = df_f[df_f["PaymentMethod"].isin(selected_pms)]
if selected_status:
    df_f = df_f[df_f["Status"].isin(selected_status)]
if selected_amount is not None and "Amount" in df_f.columns:
    df_f = df_f[(df_f["Amount"] >= selected_amount[0]) & (df_f["Amount"] <= selected_amount[1])]

# ---------------------------
# Top metrics row (attractive cards)
# ---------------------------
st.subheader("Key Metrics")
k1, k2, k3, k4 = st.columns([1.4,1.4,1.4,1.4])

k1.metric("Transactions (filtered)", f"{len(df_f):,}")
if "Amount" in df_f.columns:
    total_amt = df_f["Amount"].sum(skipna=True)
    avg_amt = df_f["Amount"].mean(skipna=True)
    med_amt = df_f["Amount"].median(skipna=True)
    k2.metric("Total Amount", f"₹ {total_amt:,.2f}")
    k3.metric("Avg Amount", f"₹ {avg_amt:,.2f}")
    k4.metric("Median Amount", f"₹ {med_amt:,.2f}")
else:
    k2.metric("Total Amount", "-")
    k3.metric("Avg Amount", "-")
    k4.metric("Median Amount", "-")

st.markdown("_")

# ---------------------------
# Visuals: trend, payment method, types, merchants, heatmap hour
# ---------------------------
st.markdown("## Visualizations")

# 1. Monthly trend (Amount by YearMonth)
if "YearMonth" in df_f.columns and "Amount" in df_f.columns:
    st.markdown("### Monthly trend — Total transaction amount")
    trend = df_f.groupby("YearMonth", as_index=False)["Amount"].sum().sort_values("YearMonth")
    fig_trend = px.line(trend, x="YearMonth", y="Amount", markers=True, template="plotly_white",
                        title="Total Amount by Month",
                        labels={"YearMonth":"Month","Amount":"Total Amount (₹)"})
    fig_trend.update_traces(line=dict(width=3, color="#0b66c2"))
    st.plotly_chart(fig_trend, use_container_width=True)

# 2. Payment Method counts & Transaction Type
col1, col2 = st.columns([1.2,1])

with col1:
    if "PaymentMethod" in df_f.columns:
        st.markdown("#### Payment Method — counts")
        pm = df_f["PaymentMethod"].value_counts().reset_index()
        pm.columns = ["PaymentMethod","count"]
        fig_pm = px.bar(pm, x="PaymentMethod", y="count", template="plotly_white",
                        labels={"count":"Count","PaymentMethod":"Payment Method"},
                        title="Payment Method (by count)")
        fig_pm.update_traces(marker_color="#0b66c2")
        st.plotly_chart(fig_pm, use_container_width=True)
    elif "BankNameSent" in df_f.columns:
        st.markdown("#### Sending Bank — counts")
        bk = df_f["BankNameSent"].value_counts().reset_index()
        bk.columns = ["Bank","count"]
        fig_bk = px.bar(bk, x="Bank", y="count", template="plotly_white", title="Sending Bank (by count)")
        fig_bk.update_traces(marker_color="#0b66c2")
        st.plotly_chart(fig_bk, use_container_width=True)

with col2:
    if "TransactionType" in df_f.columns:
        st.markdown("#### Transaction Type — distribution")
        tt = df_f["TransactionType"].value_counts().reset_index()
        tt.columns = ["TransactionType","count"]
        fig_tt = px.pie(tt, names="TransactionType", values="count", template="plotly_white",
                        title="Transaction Type Share", hole=0.4)
        st.plotly_chart(fig_tt, use_container_width=True)

# 3. Top merchants by amount
st.markdown("### Top Merchants (by transaction amount)")
if "MerchantName" in df_f.columns and "Amount" in df_f.columns:
    top_merch = df_f.groupby("MerchantName", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False).head(10)
    fig_merch = px.bar(top_merch, x="MerchantName", y="Amount", template="plotly_white",
                       labels={"Amount":"Total Amount (₹)","MerchantName":"Merchant"},
                       title="Top 10 Merchants by Amount")
    fig_merch.update_traces(marker_color="#0b66c2")
    fig_merch.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_merch, use_container_width=True)

# 4. Scatter relationships
st.markdown("### Scatter: Amount vs (Remaining Balance or Customer Age)")
if "Amount" in df_f.columns:
    scatter_x = None
    candidates = []
    if "RemainingBalance" in df_f.columns:
        candidates.append("RemainingBalance")
    if "CustomerAge" in df_f.columns:
        candidates.append("CustomerAge")
    if candidates:
        scatter_x = st.selectbox("Select X axis for scatter", options=candidates)
        color_opt = st.selectbox("Color by (categorical)", options=[None] + df_f.select_dtypes(exclude=[np.number]).columns.tolist(), index=0)
        fig_sc = px.scatter(df_f, x=scatter_x, y="Amount", color=color_opt, template="plotly_white",
                            trendline="ols" if st.checkbox("Add trendline", value=False) else None,
                            title=f"Amount vs {scatter_x}")
        st.plotly_chart(fig_sc, use_container_width=True)

# 5. Heatmap: Hour vs Day of week (if Hour exists)
if "Hour" in df_f.columns and df_f["Hour"].notna().sum() > 0:
    st.markdown("### Heatmap — Activity by hour & weekday")
    df_f["Weekday"] = df_f["TransactionDate"].dt.day_name() if "TransactionDate" in df_f.columns else ""
    heat = df_f.groupby(["Weekday","Hour"], as_index=False).size().rename(columns={"size":"count"})
    pivot = heat.pivot(index="Hour", columns="Weekday", values="count").fillna(0)
    weekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = pivot.reindex(columns=[d for d in weekdays if d in pivot.columns], fill_value=0)
    fig_heat = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="Blues"))
    fig_heat.update_layout(xaxis_title="Weekday", yaxis_title="Hour of day", template="plotly_white")
    st.plotly_chart(fig_heat, use_container_width=True)

# ---------------------------
# Data preview and download
# ---------------------------
st.markdown("## Data preview")
st.dataframe(df_f.sample(min(200, len(df_f))).reset_index(drop=True))

csv = df_f.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data (CSV)", csv, file_name="filtered_upi_transactions.csv", mime="text/csv")

st.markdown("---")
st.markdown(
    """
*About this project:* Built with Python (pandas, plotly, streamlit).  
*Author:* Neha Gadge — Data Analyst portfolio project.
"""
)
