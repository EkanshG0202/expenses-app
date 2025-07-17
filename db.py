import os
import uuid
import pandas as pd
from supabase import create_client, Client

# Replace with your actual values
SUPABASE_URL = "https://jdlpvzitixrwmipseqcc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkbHB2eml0aXhyd21pcHNlcWNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3MjY5NjcsImV4cCI6MjA2ODMwMjk2N30.AAVPvGApxbeP9Y1lPEPrUBplyK8fXOvjrB4xDAYjadc"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_transactions():
    response = supabase.table("transactions").select("*").execute()
    return pd.DataFrame(response.data)

def insert_transaction(date, description, amount, category):
    new_entry = {
        "id": str(uuid.uuid4()),
        "date": date,
        "description": description,
        "amount": amount,
        "category": category
    }
    supabase.table("transactions").insert(new_entry).execute()

def update_category(transaction_id, new_category):
    supabase.table("transactions").update({"category": new_category}).eq("id", transaction_id).execute()