
import streamlit as st
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

st.set_page_config(page_title="Smart Expense Categorizer", layout="wide")
st.title("📊 Expense Categorization App")

# Load the trained model
if os.path.exists("model.joblib"):
    model = joblib.load("model.joblib")
else:
    model = None
THRESHOLD = 0.3

uploaded_file = st.file_uploader("Upload your expenses CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Data")
    st.dataframe(df)

    if "Description" not in df.columns:
        st.error("CSV must have a 'Description' column.")
    else:
        if model:
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
        else:
            df["Predicted_Category"] = "Misc"
            df["Confidence"] = 0.0

        st.subheader("📌 Categorized Data")
        st.dataframe(df)

        misc_df = df[df["Predicted_Category"] == "Misc"].copy()
        corrected_misc = []

        if not misc_df.empty:
            st.subheader("🛠️ Manual Classification for 'Misc' Entries")
            for idx, row in misc_df.iterrows():
                selected = st.selectbox(
                    f"Description: {row['Description']}",
                    options=["Food", "Transport", "Groceries", "Subscriptions", "Utilities", "Entertainment", "Misc"],
                    key=idx
                )
                if selected != "Misc":
                    corrected_misc.append({
                        "Date": row["Date"],
                        "Description": row["Description"],
                        "Amount": row["Amount"],
                        "Category": selected
                    })
                df.at[idx, "Predicted_Category"] = selected

            if corrected_misc:
                st.subheader("📤 Save Corrected Entries for Retraining")
                corrected_df = pd.DataFrame(corrected_misc)
                st.download_button(
                    label="Download corrected_misc.csv",
                    data=corrected_df.to_csv(index=False).encode("utf-8"),
                    file_name="corrected_misc.csv",
                    mime="text/csv"
                )

                try:
                    # Load the original labeled data
                    if os.path.exists("expenses_labeled.csv"):
                        df_main = pd.read_csv("expenses_labeled.csv")
                    else:
                        df_main = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])

                    # Merge and save
                    df_merged = pd.concat([df_main, corrected_df]).drop_duplicates(subset=["Date", "Description", "Amount"])
                    df_merged.to_csv("expenses_labeled.csv", index=False)

                    # Retrain
                    X = df_merged["Description"]
                    y = df_merged["Category"]

                    pipeline = Pipeline([
                        ("tfidf", TfidfVectorizer()),
                        ("clf", LogisticRegression(max_iter=1000))
                    ])
                    pipeline.fit(X, y)
                    joblib.dump(pipeline, "model.joblib")

                    st.success("✅ Model retrained and saved!")
                except Exception as e:
                    st.warning(f"⚠️ Could not retrain model: {e}")

        st.subheader("📥 Download Final Categorized CSV")
        st.download_button(
            label="Download categorized_expenses.csv",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="categorized_expenses.csv",
            mime="text/csv"
        )
