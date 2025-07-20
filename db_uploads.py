import pandas as pd
from supabase import create_client, Client

# ✅ Replace with your actual credentials
SUPABASE_URL = "https://jdlpvzitixrwmipseqcc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkbHB2eml0aXhyd21pcHNlcWNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3MjY5NjcsImV4cCI6MjA2ODMwMjk2N30.AAVPvGApxbeP9Y1lPEPrUBplyK8fXOvjrB4xDAYjadc"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Insert a transaction (linked to a user)
def insert_parsed_transaction(user_id, date, description, amount, category):
    try:
        new_entry = {
            "user_id": user_id,
            "date": date,
            "description": description,
            "amount": amount,
            "category": category
        }
        response = supabase.table("expense_uploads").insert(new_entry).execute()
        print("✅ Inserted into expense_uploads:", response)
        return response
    except Exception as e:
        print("❌ insert_parsed_transaction failed:", e)
        raise e

# ✅ Fetch only transactions for this user
def fetch_uploaded_expenses(user_id):
    response = (
        supabase.table("expense_uploads")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return pd.DataFrame(response.data)

# ✅ Update only the given user’s row
def update_uploaded_category(user_id, id, category):
    supabase.table("expense_uploads").update({"category": category}).eq("user_id", user_id).eq("id", id).execute()
