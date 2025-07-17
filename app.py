import streamlit as st
import pandas as pd
import sys
import sklearn
from classifier import train_model, classify_transaction
from db import fetch_transactions, insert_transaction, update_category

st.title("💰 Smart Expense Tracker")
st.write("Welcome to the main dashboard! Use the sidebar to navigate.")


# ✅ Streamlit App Config
#st.set_page_config(page_title="Smart Expense Classifier", layout="wide")
#st.title("💸 Smart Expense Classifier with Supabase")

# ✅ Fetch transactions from Supabase
df = fetch_transactions()

if df.empty:
    st.warning("⚠️ No transactions found in Supabase.")
    st.stop()

# ✅ Drop rows with missing required columns
required_cols = ["id", "description", "amount", "category"]
df = df[[col for col in required_cols if col in df.columns.tolist()]]

# ✅ Train model on labeled data
train_data = df[df["category"] != "misc"]
if not train_data.empty:
    model = train_model(df=train_data)
else:
    st.warning("⚠️ No labeled data to train model.")
    model = None

# ✅ Predict categories for 'misc' transactions
if model is not None:
    df["predicted_category"] = df.apply(
        lambda row: classify_transaction(model, row["description"])
        if row["category"] == "misc" else row["category"],
        axis=1
    )

# ✅ Review and confirm predictions
misc_df = df[df["category"] == "misc"]
if not misc_df.empty and model is not None:
    st.subheader("🔍 Review Predicted Categories for 'misc' Transactions")
    for index, row in misc_df.iterrows():
        st.write(f"💬 **{row['description']}** - ₹{row['amount']}")
        predicted = row["predicted_category"]
        new_cat = st.selectbox(
            "Select correct category:",
            ["food", "subscriptions", "transport", "shopping", "utilities", "misc"],
            index=["food", "subscriptions", "transport", "shopping", "utilities", "misc"].index(predicted),
            key=f"select_{index}"
        )
        if st.button("✅ Confirm Category", key=f"btn_{index}"):
            update_category(row["id"], new_cat)
            st.success(f"Updated category to **{new_cat}**!")
            st.rerun()

# ✅ Add new transaction
st.markdown("---")
st.subheader("➕ Add New Expense")
desc = st.text_input("Description")
amt = st.number_input("Amount (₹)", min_value=1.0)
cat = st.selectbox("Category", ["misc", "food", "subscriptions", "transport", "shopping", "utilities"])
if st.button("Add Transaction"):
    if desc and amt:
        insert_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), desc, amt, cat)
        st.success("✅ Added new transaction!")
        st.rerun()
    else:
        st.error("Please enter a description and amount.")
