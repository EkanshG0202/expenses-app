import pandas as pd
from db import supabase
import time

# === CSV CONFIG ===
csv_path = "Model Training Data/Dataset 2.csv"
COLUMN_DATE = "Date"
COLUMN_AMOUNT = "Amount"
COLUMN_OLD_DESCRIPTION = "Note"       # Previously inserted column
COLUMN_NEW_DESCRIPTION = "Subcategory"  # New column to replace 'description'

# === Load CSV ===
df = pd.read_csv(csv_path)

# === Optional: Clean strings ===
df[COLUMN_OLD_DESCRIPTION] = df[COLUMN_OLD_DESCRIPTION].astype(str).str.strip()
df[COLUMN_NEW_DESCRIPTION] = df[COLUMN_NEW_DESCRIPTION].astype(str).str.strip()

# === Iterate over rows and update matching entries ===
success, failed = 0, 0

for _, row in df.iterrows():
    try:
        # Match based on date, amount, and old description
        date = pd.to_datetime(row[COLUMN_DATE]).strftime("%Y-%m-%d")
        amount = float(row[COLUMN_AMOUNT])
        old_desc = row[COLUMN_OLD_DESCRIPTION]
        new_desc = row[COLUMN_NEW_DESCRIPTION]

        # Find matching entry
        match = supabase.table("transactions")\
            .select("id")\
            .eq("date", date)\
            .eq("amount", amount)\
            .eq("description", old_desc)\
            .execute()

        if match.data:
            entry_id = match.data[0]['id']

            # Update the description to new value
            supabase.table("transactions")\
                .update({"description": new_desc})\
                .eq("id", entry_id)\
                .execute()

            print(f"✅ Updated: {old_desc} → {new_desc}")
            success += 1
        else:
            print(f"❌ No match found for: {old_desc}, {amount}, {date}")
            failed += 1

        time.sleep(0.05)  # Small delay to avoid rate limits

    except Exception as e:
        print(f"Error processing row: {e}")
        failed += 1

print(f"\n✅ Total Updated: {success}")
if failed:
    print(f"❌ Total Failed: {failed}")
