# classifier.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

MISC_THRESHOLD = 0.3  # Confidence threshold

def train_model(csv_path="expenses_labeled.csv", model_path="model.joblib"):
    df = pd.read_csv(csv_path)
    X = df["Description"]
    y = df["Category"]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X, y)
    joblib.dump(pipeline, model_path)
    print("✅ Model trained and saved.")


def predict_categories(descriptions, model_path="model.joblib"):
    pipeline = joblib.load(model_path)
    probs = pipeline.predict_proba(descriptions)
    labels = pipeline.classes_

    results = []
    for i, prob in enumerate(probs):
        top_idx = prob.argmax()
        confidence = prob[top_idx]
        predicted = labels[top_idx] if confidence >= MISC_THRESHOLD else "Misc"
        results.append((descriptions[i], predicted, confidence))

    return pd.DataFrame(results, columns=["Description", "Predicted_Category", "Confidence"])


if __name__ == "__main__":
    train_model()
    # Example prediction
    sample = ["McDonalds Takeout"]
    df = predict_categories(sample)
    print(df)
