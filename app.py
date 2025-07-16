import streamlit as st
import pandas as pd
import joblib

# Load the trained model
model = joblib.load("model.joblib")
THRESHOLD = 0.3  # Confidence cutoff for Misc category

st.set_page_config(page_title="Smart Expense Categorizer", layout="wide")
st.title("📊 Expense Categorization App")

# File uploader
uploaded_file = st.file_uploader("Upload your expenses CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Data")
    st.dataframe(df)

    # Ensure required columns
    if "Description" not in df.columns:
        st.error("CSV must have a 'Description' column.")
    else:
        # Predict categories
        probs = model.predict_proba(df["Description"])
        labels = model.classes_
        predicted = []
        confidence = []

        for i, prob in enumerate(probs):
            top_idx = prob.argmax()
            conf = prob[top_idx]
            label = labels[top_idx] if conf >= THRESHOLD else "Misc"
            predicted.append(label)
            confidence.append(conf)

        df["Predicted_Category"] = predicted
        df["Confidence"] = confidence

        st.subheader("📌 Categorized Data")
        st.dataframe(df)

        # Filter for "Misc" entries
        misc_df = df[df["Predicted_Category"] == "Misc"].copy()

        if not misc_df.empty:
            st.subheader("🛠️ Manual Classification for 'Misc' Entries")
            for idx, row in misc_df.iterrows():
                selected = st.selectbox(
                    f"Description: {row['Description']}",
                    options=["Food", "Transport", "Groceries", "Subscriptions", "Utilities", "Entertainment", "Misc"],
                    key=idx
                )
                df.at[idx, "Predicted_Category"] = selected

        # Download button
        st.subheader("📥 Download Updated Data")
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="categorized_expenses.csv",
            mime="text/csv"
        )
