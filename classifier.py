import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

MISC_THRESHOLD = 0.3  # Confidence threshold
MODEL_PATH = "model.joblib"

def train_model(df=None, csv_path="expenses_labeled.csv", model_path=MODEL_PATH):
    if df is None:
        df = pd.read_csv(csv_path)

    X = df["description"]  # lowercase, since your Supabase column is likely 'description'
    y = df["category"]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X, y)
    joblib.dump(pipeline, model_path)
    print("✅ Model trained and saved.")

    return pipeline  # Return model for reuse

def predict_categories(descriptions, model_path=MODEL_PATH):
    pipeline = joblib.load(model_path)
    probs = pipeline.predict_proba(descriptions)
    labels = pipeline.classes_

    results = []
    for i, prob in enumerate(probs):
        top_idx = prob.argmax()
        confidence = prob[top_idx]
        predicted = labels[top_idx] if confidence >= MISC_THRESHOLD else "misc"
        results.append((descriptions[i], predicted, confidence))

    return pd.DataFrame(results, columns=["description", "predicted_category", "confidence"])

def classify_transaction(description, model_path=MODEL_PATH):
    df = predict_categories([description], model_path=model_path)
    return df["predicted_category"].iloc[0]  # Only return predicted label

# Optional CLI usage
if __name__ == "__main__":
    train_model()
    sample = ["McDonalds Takeout"]
    df = predict_categories(sample)
    print(df)
