import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.utils import resample
import joblib
import re

MODEL_PATH = "model.joblib"
MISC_THRESHOLD = 0.2

# Text cleaning
def clean_text(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r"[^\w\s]", "", text.lower().strip())


# Train model
def train_model(df=None, csv_path="expenses_labeled.csv", model_path=MODEL_PATH):
    if df is None:
        df = pd.read_csv(csv_path)

    # Clean text
    df = df.dropna(subset=["description", "category"])  # Drop rows with missing values
    df["description"] = df["description"].apply(clean_text)


    # Save original for lookup
    
    df[["description", "category"]].to_csv("training_lookup.csv", index=False)

    # Handle imbalance by oversampling
    max_size = df["category"].value_counts().max()
    dfs = [resample(g, replace=True, n_samples=max_size, random_state=42)
           for _, g in df.groupby("category")]
    df_balanced = pd.concat(dfs)

    X = df_balanced["description"]
    y = df_balanced["category"]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(
            solver="lbfgs",
            multi_class="multinomial",
            max_iter=1000,
            class_weight="balanced"
        ))
    ])

    pipeline.fit(X, y)
    joblib.dump(pipeline, model_path)
    print("✅ Model trained and saved with exact match support.")
    return pipeline

# Hybrid predictor: exact match or model prediction
def predict_categories(descriptions, model_path=MODEL_PATH, lookup_path="training_lookup.csv"):
    pipeline = joblib.load(model_path)
    lookup_df = pd.read_csv(lookup_path)
    lookup_map = {clean_text(d): c for d, c in zip(lookup_df["description"], lookup_df["category"])}

    cleaned = [clean_text(d) for d in descriptions]
    probs = pipeline.predict_proba(cleaned)
    labels = pipeline.classes_

    results = []
    for i, desc in enumerate(cleaned):
        orig_desc = descriptions[i]
        if desc in lookup_map:
            results.append((orig_desc, lookup_map[desc], 1.0))
        else:
            top_idx = probs[i].argmax()
            confidence = probs[i][top_idx]
            predicted = labels[top_idx] if confidence >= MISC_THRESHOLD else "misc"
            results.append((orig_desc, predicted, confidence))

    return pd.DataFrame(results, columns=["description", "predicted_category", "confidence"])

# Single inference
def classify_transaction(description, model_path=MODEL_PATH):
    df = predict_categories([description], model_path=model_path)
    return df["predicted_category"].iloc[0], df["confidence"].iloc[0]

# CLI test
if __name__ == "__main__":
    train_model()
    test = ["Swiggy dinner", "Uber ride", "Netflix", "Some unknown thing"]
    out = predict_categories(test)
    print(out)
