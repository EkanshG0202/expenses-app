import pandas as pd
import uuid
from db import supabase  # Make sure supabase client is properly configured
from datetime import datetime

# === Step 1: Load the CSV ===
csv_path = "Model Training Data/Dataset 2.csv"  # ← CHANGE THIS TO YOUR CSV FILE PATH
df = pd.read_csv(csv_path)

# === Step 2: Manually specify the relevant columns ===
COLUMN_DATE = "Date"          # change as per your CSV
COLUMN_DESCRIPTION = "Note"   # change as per your CSV
COLUMN_AMOUNT = "Amount"      # change as per your CSV
COLUMN_CATEGORY = "Category"  # change as per your CSV

# === Step 3: Data cleaning ===
def clean_row(row):
    try:
        return {
            "id": str(uuid.uuid4()),
            "date": pd.to_datetime(row[COLUMN_DATE]).strftime("%Y-%m-%d"),
            "description": str(row[COLUMN_DESCRIPTION]).strip(),
            "amount": float(row[COLUMN_AMOUNT]),
            "category": str(row[COLUMN_CATEGORY]).lower().strip()
        }
    except Exception as e:
        print(f"Skipping row due to error: {e}")
        return None

# === Step 4: Process and upload ===
entries = df.apply(clean_row, axis=1).dropna()

success, failed = 0, 0

for entry in entries:
    try:
        supabase.table("transactions").insert(entry).execute()
        success += 1
    except Exception as e:
        print(f"Insert failed for entry: {entry}\nError: {e}")
        failed += 1

print(f"\n✅ Uploaded: {success} rows")
if failed:
    print(f"❌ Failed: {failed} rows")
