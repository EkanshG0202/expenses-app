import streamlit as st
import pandas as pd
from classifier import train_model, classify_transaction
from db import fetch_transactions, insert_transaction, update_category
from db_uploads import fetch_uploaded_expenses, insert_parsed_transaction
from supabase import create_client

# Make sure this runs only if user is logged in
if "user_id" not in st.session_state:
    st.error("Please log in to continue.")
    st.stop()

user_id = st.session_state.user_id

st.markdown("---")
st.subheader("➕ Add New Transaction")

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
            insert_parsed_transaction(user_id, pd.Timestamp.now().strftime("%Y-%m-%d"), desc, amt, st.session_state["predicted_cat"])
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
    manual_cat = st.selectbox("Select category", [
        "Food", "Subscriptions", "Transport", "Shopping", "Utilities", "Misc",
        "Entertainment", "Medicine", "Personal", "Education", "Investments", "Work","Income"
    ], key="manual_cat_select")

    if st.button("Confirm Category"):
        try:
            insert_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), desc, amt, manual_cat)
            insert_parsed_transaction(user_id, pd.Timestamp.now().strftime("%Y-%m-%d"), desc, amt, manual_cat)
            st.success(f"✅ Added with selected category: **{manual_cat}**")
        except Exception as e:
            st.error(f"Insertion failed: {e}")
        for key in ["desc", "amt", "awaiting_manual_category"]:
            st.session_state.pop(key, None)
        st.rerun()
