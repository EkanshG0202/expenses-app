import streamlit as st
import pandas as pd
import time
from classifier import train_model, classify_transaction
from db import fetch_transactions, insert_transaction, update_category
from db_uploads import fetch_uploaded_expenses, insert_parsed_transaction

st.title("💰 Smart Expense Tracker")
st.write("Welcome to the main dashboard! Use the sidebar to navigate.")

# ✅ Caching to speed up reruns
@st.cache_data(show_spinner="Fetching transactions...")
def get_transactions():
    return fetch_transactions()

df = get_transactions()

if df.empty:
    st.warning("⚠️ No transactions found in Supabase.")
    st.stop()

required_cols = ["id", "description", "amount", "category"]
df = df[[col for col in required_cols if col in df.columns.tolist()]]

train_data = df[df["category"] != "misc"]

@st.cache_resource(show_spinner="Training model...")
def get_model(train_data):
    return train_model(df=train_data)

model = get_model(train_data) if not train_data.empty else None
if model is None:
    st.warning("⚠️ No labeled data to train model.")

# ✅ Only predict once for all 'misc' rows
if model is not None:
    misc_df = df[df["category"] == "misc"].copy()
    if not misc_df.empty:
        st.subheader("🔍 Review Predicted Categories for 'misc' Transactions")
        misc_df["predicted_category"] = misc_df["description"].apply(lambda desc: classify_transaction(model, desc))
        for index, row in misc_df.iterrows():
            st.write(f"💬 **{row['description']}** - ₹{row['amount']}")
            new_cat = st.selectbox(
                "Select correct category:",
                ["food", "subscriptions", "transport", "shopping", "utilities", "misc"],
                index=["food", "subscriptions", "transport", "shopping", "utilities", "misc"].index(row["predicted_category"]),
                key=f"select_{index}"
            )
            if st.button("✅ Confirm Category", key=f"btn_{index}"):
                update_category(row["id"], new_cat)
                st.success(f"Updated category to **{new_cat}**!")
                st.rerun()

# ✅ Add New Transaction
st.markdown("---")
st.subheader("➕ Add New Expense")

desc = st.text_input("Description", value=st.session_state.get("desc", ""))
amt = st.number_input("Amount", value=st.session_state.get("amt", 0.0))

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
            st.session_state["awaiting_manual_category"] = False
        else:
            st.session_state["awaiting_manual_category"] = True
            st.session_state["awaiting_confirmation"] = False
    else:
        st.error("Please enter both description and amount.")

# ✅ Confirmation or manual category
if st.session_state.get("awaiting_confirmation", False):
    st.write(f"💡 Predicted category: **{st.session_state['predicted_cat']}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm Prediction"):
            insert_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), desc, amt, st.session_state["predicted_cat"])
            insert_parsed_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), desc, amt, st.session_state["predicted_cat"])
            st.success(f"✅ Added with predicted category: **{st.session_state['predicted_cat']}**")
            for key in ["desc", "amt", "awaiting_confirmation", "predicted_cat", "confidence"]:
                st.session_state.pop(key, None)
            st.rerun()
    with col2:
        if st.button("❌ Choose Another"):
            st.session_state["awaiting_manual_category"] = True
            st.session_state["awaiting_confirmation"] = False
            st.rerun()

if st.session_state.get("awaiting_manual_category", False):
    st.warning("⚠️ Low confidence in prediction or predicted 'misc'. Please choose a category.")
    manual_cat = st.selectbox("Select category", ["Food", "Subscriptions", "Transport", "Shopping", "Utilities", "Misc","Entertainment","Medicine","Personal","Education","Investments","Work"], key="manual_cat_select")

    if st.button("Confirm Category"):
        try:
            insert_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), desc, amt, manual_cat)
            insert_parsed_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), desc, amt, manual_cat)
            st.success(f"✅ Added with selected category: **{manual_cat}**")
        except Exception as e:
            st.error(f"Insertion failed: {e}")
        for key in ["desc", "amt", "awaiting_manual_category"]:
            st.session_state.pop(key, None)
        st.rerun()
