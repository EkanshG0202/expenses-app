import streamlit as st
import pandas as pd
import plotly.express as px
from db_uploads import fetch_uploaded_expenses

user_id = st.session_state.get("user_id")

# --- Page config (Only set ONCE and at the TOP) ---
st.set_page_config(page_title="Spending Analytics", page_icon="📊", layout="wide")
st.title("📈 Spending Analytics Dashboard")

# --- Load data ---
df = fetch_uploaded_expenses(user_id)

if df.empty:
    st.warning("No transactions found. Please upload data first.")
    st.stop()

# --- Preprocess ---
df["date"] = pd.to_datetime(df["date"], errors='coerce')
df = df.dropna(subset=["date", "amount", "category"])
df = df.sort_values("date")

# --- Normalize categories ---
def normalize_category(cat):
    cat = cat.strip().lower()
    if "transport" in cat or "trandport" in cat or "transportation" in cat:
        return "Transport"
    elif "food" in cat:
        return "Food"
    elif "shopping" in cat:
        return "Shopping"
    elif "subscr" in cat:
        return "Subscriptions"
    elif "medic" in cat:
        return "Medicine"
    elif "utilit" in cat:
        return "Utilities"
    elif "entertain" in cat:
        return "Entertainment"
    elif "educat" in cat:
        return "Education"
    elif "invest" in cat:
        return "Investments"
    elif "work" in cat:
        return "Work"
    elif "personal" in cat:
        return "Personal"
    elif "income" in cat:
        return "Income"
    else:
        return "Misc"

df["category"] = df["category"].apply(normalize_category)

# --- Separate Income from Expenses ---
income_df = df[df["category"] == "Income"]
df = df[df["category"] != "Income"]

# --- Income Summary ---
if not income_df.empty:
    st.header("💰 Income Summary")
    total_income = income_df["amount"].sum()
    st.metric("Total Income", f"₹{total_income:,.2f}")
    with st.expander("📄 Income Transactions"):
        st.dataframe(income_df.reset_index(drop=True))

# --- Expense Metrics ---
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

# --- Top Descriptions / Merchants ---
st.subheader("🏪 Top Descriptions / Merchants")
top_desc = df["description"].value_counts().head(5)
st.bar_chart(top_desc)

# --- Raw Data Option ---
with st.expander("📋 Show Raw Transactions"):
    st.dataframe(df.reset_index(drop=True))
