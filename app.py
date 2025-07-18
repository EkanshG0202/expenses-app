import streamlit as st
import pandas as pd
import sys
import sklearn
from classifier import train_model, classify_transaction
from db import fetch_transactions, insert_transaction, update_category
from db_uploads import fetch_uploaded_expenses, insert_parsed_transaction
import time

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
if "desc" not in st.session_state:
    st.session_state["desc"] = ""
if "amt" not in st.session_state:
    st.session_state["amt"] = 0.0

desc = st.text_input("Description", value=st.session_state["desc"])
amt = st.number_input("Amount", value=st.session_state["amt"])

# On submit, save desc and amt into session state
if st.button("Add Transaction"):
    if desc and amt:
        st.session_state["desc"] = desc
        st.session_state["amt"] = amt

        predicted_cat, confidence = classify_transaction(desc)
        st.session_state["predicted_cat"] = predicted_cat
        st.session_state["confidence"] = confidence

        st.info(f"🧠 Model Prediction: **{predicted_cat}** with confidence **{confidence*100:.2f}%**")

        if predicted_cat != "misc" and confidence > 0.25:
            st.session_state["awaiting_confirmation"] = True
        else:
            st.session_state["awaiting_manual_category"] = True
    else:
        st.error("Please enter both description and amount.")

# ✅ If model predicted confidently, ask for confirmation
if st.session_state.get("awaiting_confirmation", False):
    st.write(f"💡 Predicted category: **{st.session_state['predicted_cat']}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm Prediction"):
            insert_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), st.session_state["desc"], st.session_state["amt"], st.session_state["predicted_cat"])
            insert_parsed_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), st.session_state["desc"], st.session_state["amt"], st.session_state["predicted_cat"])
            st.success(f"✅ Added with predicted category: **{st.session_state['predicted_cat']}**")

            # Reset state
            st.session_state["desc"] = ""
            st.session_state["amt"] = 0.0
            st.session_state["awaiting_confirmation"] = False

    with col2:
        if st.button("❌ Choose Another"):
            st.session_state["awaiting_confirmation"] = False
            st.session_state["awaiting_manual_category"] = True


# Show manual category if model was unsure
if st.session_state.get("awaiting_manual_category", False):
    st.warning("⚠️ Low confidence in prediction or predicted 'misc'. Please choose a category.")
    manual_cat = st.selectbox("Select category", ["Food", "Subscriptions", "Transport", "Shopping", "Utilities", "misc"], key="manual_cat_select")

    if st.button("Confirm Category"):
        try:
            insert_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), st.session_state["desc"], st.session_state["amt"], manual_cat)
            insert_parsed_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), st.session_state["desc"], st.session_state["amt"], manual_cat)
            st.success(f"✅ Added with selected category: **{manual_cat}**")
        except Exception as e:
            st.error(f"Insertion failed: {e}")
        
        # Clear session state
        st.session_state["awaiting_manual_category"] = False
        st.session_state["desc"] = ""
        st.session_state["amt"] = 0.0
    else:
        st.error("Please enter a description and amount.")



