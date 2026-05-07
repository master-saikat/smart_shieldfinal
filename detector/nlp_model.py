import os
import joblib

# Load model relative to this file — works regardless of where Django is started from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, "scam_model.pkl"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "vectorizer.pkl"))


def predict_scam(text):
    # Enforce input length limit
    text = text[:2000]

    X = vectorizer.transform([text])
    prediction = model.predict(X)[0]
    prob = model.predict_proba(X)[0][1]
    risk = int(prob * 100)

    if prediction == 0:
        label = "Safe"
    elif risk < 70:
        label = "Suspicious"
    else:
        label = "Dangerous"   # unified label — was "Scam", now matches link checker

    return risk, label