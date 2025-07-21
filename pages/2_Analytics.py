import streamlit as st
import pandas as pd
import plotly.express as px
from db_uploads import fetch_uploaded_expenses
from db_budgets import get_budget, set_budget, reset_budget


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

# --- Month Selector ---
df["month"] = df["date"].dt.to_period("M").astype(str)
available_months = sorted(df["month"].unique(), reverse=True)
selected_month = st.selectbox("🗓️ Select Month", available_months)
df = df[df["month"] == selected_month]

# --- Monthly Budget Section ---
# --- Monthly Budget Section ---
st.subheader("📉 Monthly Budget")

stored_budget = get_budget(user_id, selected_month)

if stored_budget is None:
    input_budget = st.number_input("Enter your budget for this month (₹):", min_value=0.0, format="%.2f")
    if input_budget > 0:
        set_budget(user_id, selected_month, input_budget)
        st.success(f"Budget of ₹{input_budget:,.2f} set for {selected_month}.")
        st.rerun()
else:
    spent = df[df["category"].str.lower() != "income"]["amount"].sum()
    remaining = stored_budget - spent
    percent = min(spent / stored_budget, 1.0) if stored_budget > 0 else 0

    st.metric("💼 Budget", f"₹{stored_budget:,.2f}")
    st.metric("💸 Spent", f"₹{spent:,.2f}")
    st.progress(percent, text=f"{percent*100:.1f}% of your budget used")

    if remaining > 0:
        st.info(f"You are ₹{remaining:,.2f} away from your budget.")
    else:
        st.error(f"⚠️ You have exceeded your budget by ₹{-remaining:,.2f}!")

    if st.button("Reset Budget"):
        reset_budget(user_id, selected_month)
        st.rerun()


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
monthly_avg = total_spent  # Since we're filtering by a single month
category_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)

col1, col2 = st.columns(2)
col1.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
col2.metric("📆 Monthly Total", f"₹{monthly_avg:,.2f}")

# --- Category Breakdown ---
st.subheader("📊 Spending by Category")
fig1 = px.pie(
    names=category_totals.index,
    values=category_totals.values,
    title=f"Distribution by Category - {selected_month}",
    hole=0.4
)
st.plotly_chart(fig1, use_container_width=True)

# --- Daily Spending Trend ---
st.subheader("📅 Daily Spending Trend")
daily = df.resample("D", on="date")["amount"].sum().reset_index()
fig2 = px.bar(daily, x="date", y="amount", title="Spending Per Day")
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
