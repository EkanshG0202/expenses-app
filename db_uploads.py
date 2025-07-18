import pandas as pd
from supabase import create_client, Client

# ✅ Replace with your actual credentials
SUPABASE_URL = "https://jdlpvzitixrwmipseqcc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkbHB2eml0aXhyd21pcHNlcWNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3MjY5NjcsImV4cCI6MjA2ODMwMjk2N30.AAVPvGApxbeP9Y1lPEPrUBplyK8fXOvjrB4xDAYjadc"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_parsed_transaction(date, description, amount, category):
    try:
        new_entry = {
            "date": date,
            "description": description,
            "amount": amount,
            "category": category
        }
        response = supabase.table("expense_uploads").insert(new_entry).execute()
        print("✅ Inserted into expenses_upload:", response)
        return response
    except Exception as e:
        print("❌ insert_parsed_transaction failed:", e)
        raise e

def fetch_uploaded_expenses():
    response = supabase.table("expense_uploads").select("*").order("created_at", desc=True).execute()
    return pd.DataFrame(response.data)

def update_uploaded_category(id, category):
    supabase.table("expense_uploads").update({"category": category}).eq("id", id).execute()