import streamlit as st
import pandas as pd
import time
import secrets
from classifier import train_model, classify_transaction
from db import fetch_transactions, insert_transaction, update_category
from db_uploads import fetch_uploaded_expenses, insert_parsed_transaction
from supabase import create_client
from passlib.hash import pbkdf2_sha256
import os

# Supabase setup
SUPABASE_URL = "https://jdlpvzitixrwmipseqcc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkbHB2eml0aXhyd21pcHNlcWNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3MjY5NjcsImV4cCI6MjA2ODMwMjk2N30.AAVPvGApxbeP9Y1lPEPrUBplyK8fXOvjrB4xDAYjadc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Session handling
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# === Auth functions ===
def hash_password(password):
    return pbkdf2_sha256.hash(password)

def check_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)

def signup():
    st.subheader("🆕 Sign Up")
    username = st.text_input("Username", key="signup_user")
    password = st.text_input("Password", type="password", key="signup_pass")
    if st.button("Create Account"):
        res = supabase.table("users").select("*").eq("username", username).execute()
        if res.data:
            st.error("Username already exists!")
            return
        hashed_password = hash_password(password)
        supabase.table("users").insert({"username": username, "password": hashed_password}).execute()
        st.success("Account created. Please login.")

def login():
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        res = supabase.table("users").select("*").eq("username", username).execute()
        if not res.data:
            st.error("Invalid username.")
            return
        user = res.data[0]
        if check_password(password, user["password"]):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_id = user["id"]
            st.success(f"Welcome back, {username}!")
            time.sleep(1)  # Optional: let success message show
            st.switch_page("pages/1_Transactions.py")
            st.rerun()
        else:
            st.error("Incorrect password.")
user_id = st.session_state.get("user_id")

def logout():
    st.session_state.clear()
    st.rerun()

# === Auth UI ===
st.sidebar.title("🔐 User Access")
if not st.session_state.logged_in:
    auth_action = st.sidebar.radio("Choose action", ["Login", "Sign Up"])
    if auth_action == "Login":
        login()
    else:
        signup()
    st.stop()
else:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("🚪 Logout"):
        logout()

# === Main App ===
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
