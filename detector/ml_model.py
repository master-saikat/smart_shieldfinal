"""
Train the SmartShield scam detection model.

RECOMMENDED: Use a real dataset for accurate results.
Download the SMS Spam Collection dataset from:
https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset
Save it as spam.csv in this directory, then set USE_REAL_DATASET = True.

The CSV should have columns: 'v1' (ham/spam) and 'v2' (message text).
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

USE_REAL_DATASET = False   # ← set True once you download spam.csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_data():
    if USE_REAL_DATASET:
        csv_path = os.path.join(BASE_DIR, "spam.csv")
        df = pd.read_csv(csv_path, encoding="latin-1")[["v1", "v2"]]
        df.columns = ["label_str", "text"]
        df["label"] = df["label_str"].map({"ham": 0, "spam": 1})
        return df[["text", "label"]]
    else:
        # Minimal fallback — replace with real dataset for production
        data = {
            "text": [
                "Your account is blocked, click here immediately",
                "Congratulations! You have won a lottery prize",
                "Please verify your password immediately or lose access",
                "Click here to claim your free prize now",
                "Your OTP is 1234, do not share with anyone",
                "You have been selected for a cash reward",
                "Your bank account will be suspended unless you verify",
                "Win a free iPhone by clicking this link",
                "Hello, how are you doing today?",
                "Meeting scheduled for tomorrow at 10am",
                "Let's have lunch today at the usual place",
                "Please review the attached document",
                "Your package has been shipped and will arrive Friday",
                "Can you send me the report by end of day?",
                "Happy birthday! Hope you have a great day",
                "The project deadline has been extended by one week",
            ],
            "label": [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        }
        return pd.DataFrame(data)


def train():
    df = load_data()
    print(f"Dataset size: {len(df)} samples")
    print(f"Scam: {df['label'].sum()} | Safe: {(df['label'] == 0).sum()}")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    if len(X_test) > 0:
        y_pred = model.predict(X_test_vec)
        print("\nModel Performance:")
        print(classification_report(y_test, y_pred, target_names=["Safe", "Scam"]))

    joblib.dump(model, os.path.join(BASE_DIR, "scam_model.pkl"))
    joblib.dump(vectorizer, os.path.join(BASE_DIR, "vectorizer.pkl"))
    print("\nModel trained and saved successfully!")


if __name__ == "__main__":
    train()