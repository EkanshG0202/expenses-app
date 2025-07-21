# insights.py

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from db_uploads import fetch_uploaded_expenses
from db_budgets import get_budget
from llm_utils import generate_insights_llm



# --- Utility Functions ---

def get_monthly_spend(user_id, month):
    df = fetch_uploaded_expenses(user_id)
    df = df[df["category"] != "Income"]
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"].dt.strftime("%Y-%m") == month]
    return df["amount"].sum(), df

def get_category_breakdown(df):
    return df.groupby("category")["amount"].sum().sort_values(ascending=False)

def get_daily_spending(df):
    return df.groupby(df["date"].dt.date)["amount"].sum().reset_index(name="daily_spend")

def generate_saving_suggestions(breakdown, budget, total_spent):
    suggestions = []
    percent_used = (total_spent / budget) * 100 if budget else 0

    if "Food Delivery" in breakdown and breakdown["Food Delivery"] > 0.15 * budget:
        suggestions.append("🍔 High spending on food delivery. Try cooking more meals at home.")

    if "Subscriptions" in breakdown and breakdown["Subscriptions"] > 1000:
        suggestions.append("📺 Multiple subscriptions detected. Consider canceling unused ones.")

    if "Shopping" in breakdown and breakdown["Shopping"] > 0.2 * budget:
        suggestions.append("🛍️ Significant shopping expenses. Set a fixed shopping limit.")

    if percent_used > 90:
        suggestions.append("⚠️ You're close to your budget limit. Reduce discretionary spending.")

    if not suggestions:
        suggestions.append("🎉 Great job! Your spending looks healthy this month.")

    return suggestions

def generate_budget_alerts(budget, total_spent):
    percent_used = (total_spent / budget) * 100 if budget else 0
    if budget == 0:
        return "⚠️ You have not set a budget for this month. Set one to track better."
    elif percent_used > 100:
        return "🚨 You have exceeded your monthly budget!"
    elif percent_used > 90:
        return "⚠️ Warning: You are very close to your monthly budget."
    elif percent_used > 60:
        return "✅ You are doing okay, but keep an eye on your expenses."
    elif percent_used > 0:
        return "💡 You're under budget. Keep it up!"
    else:
        return "📭 You haven't spent anything this month."

# --- Page Config ---
st.set_page_config(page_title="Insights", layout="wide")
st.title("💡 Monthly Financial Insights")

# --- Session Info ---
user_id = st.session_state.get("user_id")
if not user_id:
    st.error("Please log in to view your insights.")
    st.stop()

# --- Date Context ---
month = datetime.date.today().strftime("%Y-%m")

# --- Fetch Budget and Transactions ---
budget = get_budget(user_id, month) or 0
total_spent, df = get_monthly_spend(user_id, month)
breakdown = get_category_breakdown(df)
daily_trend = get_daily_spending(df)
suggestions = generate_saving_suggestions(breakdown, budget, total_spent)
alert_message = generate_budget_alerts(budget, total_spent)

# --- Summary Section ---
st.subheader("📊 Budget Summary")
st.metric("Monthly Budget", f"₹{budget}")
st.metric("Total Spent", f"₹{total_spent}")
st.metric("Remaining", f"₹{budget - total_spent}")
st.progress(min(total_spent / budget, 1.0) if budget > 0 else 0)
st.warning(alert_message)

# --- Trend Analysis ---
st.subheader("📈 Spending Trend (Daily)")
if not daily_trend.empty:
    fig_trend = px.line(daily_trend, x="date", y="daily_spend", markers=True,
                        title="Your Daily Spending Trend")
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("No daily transactions recorded for this month.")

# --- Category Breakdown ---
st.subheader("🧾 Spending Breakdown by Category")
if not breakdown.empty:
    fig = px.pie(
        names=breakdown.index,
        values=breakdown.values,
        title="Category-wise Spending",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No transactions found for this month.")

# --- Suggestions Section ---
st.subheader("💰 Smart Saving Suggestions")
for suggestion in suggestions:
    st.info(suggestion)
    
# --- LLM-Powered Insights ---
st.subheader("🧠 AI-Generated Insights")

with st.spinner("Analyzing your transactions with AI..."):
    insights = generate_insights_llm(month, total_spent, budget, breakdown.to_dict())

st.success("Here are your personalized insights:")
st.write(insights)
