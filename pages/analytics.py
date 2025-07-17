import streamlit as st
import pandas as pd
import plotly.express as px
from db import fetch_transactions

# --- Page config (Only set ONCE and at the TOP) ---
st.set_page_config(page_title="Spending Analytics", page_icon="📊", layout="wide")
st.title("📈 Spending Analytics Dashboard")

# --- Load data ---
df = fetch_transactions()

if df.empty:
    st.warning("No transactions found. Please upload data first.")
    st.stop()

# --- Preprocess ---
df["date"] = pd.to_datetime(df["date"], errors='coerce')
df = df.dropna(subset=["date", "amount", "category"])
df = df.sort_values("date")

# --- Metrics ---
total_spent = df["amount"].sum()
monthly_avg = df.resample("M", on="date")["amount"].sum().mean()
category_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)

col1, col2 = st.columns(2)
col1.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
col2.metric("📆 Monthly Average", f"₹{monthly_avg:,.2f}")

# --- Category Breakdown ---
st.subheader("📊 Spending by Category")
fig1 = px.pie(
    names=category_totals.index,
    values=category_totals.values,
    title="Distribution by Category",
    hole=0.4
)
st.plotly_chart(fig1, use_container_width=True)

# --- Monthly Spending Trend ---
st.subheader("📅 Monthly Spending Trend")
monthly = df.resample("M", on="date")["amount"].sum().reset_index()
fig2 = px.bar(monthly, x="date", y="amount", title="Total Spending Each Month")
st.plotly_chart(fig2, use_container_width=True)

# --- Anomaly Detection ---
st.subheader("🚨 Outliers / Anomalies")
threshold = df["amount"].mean() + 2 * df["amount"].std()
outliers = df[df["amount"] > threshold]

if not outliers.empty:
    st.warning(f"Found {len(outliers)} high-value transactions above ₹{threshold:,.2f}:")
    st.dataframe(outliers)
else:
    st.success("No significant outliers found!")

# --- Top Merchants ---
st.subheader("🏪 Top Descriptions / Merchants")
top_desc = df["description"].value_counts().head(5)
st.bar_chart(top_desc)

# --- Raw Data Option ---
with st.expander("📋 Show Raw Transactions"):
    st.dataframe(df.reset_index(drop=True))
