from pathlib import Path
import csv
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "dataset" / "emails.csv"
MODEL_PATH = BASE / "model" / "spamshield_model.joblib"

texts, labels = [], []
with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        text = (row.get("text") or "").strip()
        label = (row.get("label") or "").strip().lower()
        if text and label in {"spam", "safe"}:
            texts.append(text)
            labels.append(label)

print(f"Loaded {len(texts)} messages: {dict(Counter(labels))}")
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.20, random_state=42, stratify=labels
)
model = Pipeline([
    ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english",
                              ngram_range=(1, 2), max_features=100000,
                              sublinear_tf=True)),
    ("classifier", LinearSVC(class_weight="balanced", random_state=42)),
])
model.fit(X_train, y_train)
pred = model.predict(X_test)
print(f"\nHeld-out test accuracy: {accuracy_score(y_test, pred):.4f}")
print("\nClassification report:")
print(classification_report(y_test, pred, digits=4, zero_division=0))
print("Confusion matrix (labels order: safe, spam):")
print(confusion_matrix(y_test, pred, labels=["safe", "spam"]))
MODEL_PATH.parent.mkdir(exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"\nSaved trained model to: {MODEL_PATH}")
print("Important: test results are from an older corpus and do not guarantee modern phishing detection.")
