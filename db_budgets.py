from supabase import create_client, Client
import os

# --- Supabase Setup ---
SUPABASE_URL = "https://jdlpvzitixrwmipseqcc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkbHB2eml0aXhyd21pcHNlcWNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3MjY5NjcsImV4cCI6MjA2ODMwMjk2N30.AAVPvGApxbeP9Y1lPEPrUBplyK8fXOvjrB4xDAYjadc"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Get budget for a user and month ---
def get_budget(user_id, month):
    response = supabase.table("budgets").select("budget").eq("user_id", user_id).eq("month", month).limit(1).execute()
    if response.data and len(response.data) > 0:
        return float(response.data[0]["budget"])
    return None

# --- Set or update budget for a user and month ---
def set_budget(user_id, month, budget):
    existing = supabase.table("budgets").select("budget").eq("user_id", user_id).eq("month", month).limit(1).execute()
    if existing.data and len(existing.data) > 0:
        # Update existing
        supabase.table("budgets").update({"budget": budget}).eq("user_id", user_id).eq("month", month).execute()
    else:
        # Insert new
        supabase.table("budgets").insert({"user_id": user_id, "month": month, "budget": budget}).execute()

# --- Delete/reset budget for a user and month ---
def reset_budget(user_id, month):
    supabase.table("budgets").delete().eq("user_id", user_id).eq("month", month).execute()
