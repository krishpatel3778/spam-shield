from pathlib import Path
import csv
import re
import joblib
from flask import Flask, render_template, request, jsonify, redirect, url_for
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "spamshield_model.joblib"
DATASET_PATH = BASE_DIR / "dataset" / "emails.csv"

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-development-secret-key"


def train_model():
    """Train a small starter classifier from the bundled example dataset."""
    MODEL_DIR.mkdir(exist_ok=True)
    texts, labels = [], []
    with DATASET_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip().lower()
            if text and label in {"spam", "safe"}:
                texts.append(text)
                labels.append(label)
    if len(set(labels)) < 2:
        raise RuntimeError("Dataset must contain both 'safe' and 'spam' labels.")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))),
        ("classifier", LinearSVC(class_weight="balanced", random_state=42)),
    ])
    pipeline.fit(texts, labels)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


def load_model():
    # Retrain from the expanded dataset on startup so the added corpus is actually used.
    # Delete model/spamshield_model.joblib if you later change the CSV and want a fresh fit.
    return train_model()


model = load_model()


def inspect_signals(text):
    """Return human-readable indicators found in the submitted message."""
    lower = text.lower()
    checks = [
        ("Urgency or pressure", r"\b(urgent|immediately|act now|expires today|limited time|final warning|within 24 hours)\b", "Scammers may pressure you to act quickly before you can verify the request."),
        ("Requests for credentials", r"\b(password|verify your account|login details|otp|one.time password|pin|verification code)\b", "Unexpected requests for passwords, OTPs, PINs, or login details are a serious warning sign."),
        ("Money or payment language", r"\b(payment|bank|transfer|refund|prize|winner|gift card|crypto|wire transfer|fee|account blocked)\b", "Unexpected payment demands, prizes, refunds, or account warnings can be used to trick people."),
        ("Suspicious link signal", r"(https?://|www\.|bit\.ly|tinyurl|click here|open this link)", "Links can lead to imitation websites or harmful downloads. Check the destination independently."),
        ("Unexpected attachment language", r"\b(attachment|attached file|download the file|enable macros|open the document)\b", "Unexpected attachments can contain harmful files or lead to fake login pages."),
    ]
    found = []
    for title, pattern, why in checks:
        matches = re.findall(pattern, lower, flags=re.IGNORECASE)
        if matches:
            found.append({"title": title, "why": why, "matched_text": ", ".join(dict.fromkeys(m.lower() for m in matches[:5])), "count": len(matches)})
    urls = re.findall(r"(?:https?://|www\.)\S+", text, flags=re.IGNORECASE)
    return found, urls


def predict_email(text):
    prediction = str(model.predict([text])[0]).lower()
    signals, urls = inspect_signals(text)
    # Educational heuristic only; this is not the model's probability.
    score = min(95, 12 + len(signals) * 14 + (18 if prediction == "spam" else 0))
    if prediction == "spam":
        title = "Potential spam or phishing detected"
        explanation = ("The machine-learning model classified this message as SPAM because its text patterns resemble messages labelled as spam in the training examples. Review the warning signs below before deciding what to do.")
        action = ("Do not click links, open unexpected attachments, reply with sensitive information, or send money. Verify the sender using a contact method or website you already trust.")
        interacted = ("If you clicked a link, close the page and do not enter details. If you shared a password or OTP, change affected passwords immediately, enable multi-factor authentication, and contact your bank or service provider if financial or account information was exposed.")
    else:
        title = "No spam detected by the model"
        explanation = ("The model classified this message as SAFE, meaning it did not find enough learned spam-like patterns to label it as spam. This is not proof that the sender or message is legitimate—new or carefully written scams can still pass a text classifier.")
        action = ("Check the sender address, context, and any web address independently. Never share an OTP, password, PIN, or payment details in response to an unexpected message.")
        interacted = ("If you already opened a link, avoid entering information. If you submitted credentials or financial details, change the affected password and contact the relevant provider promptly.")
    level = "HIGH" if score >= 65 else "MEDIUM" if score >= 40 else "LOW"
    return {
        "prediction": prediction.upper(), "title": title, "risk_score": score, "risk_level": level,
        "model": "TF-IDF + Linear SVM", "analysis": signals, "url_count": len(urls), "detected_urls": urls[:5],
        "message": explanation, "recommended_action": action, "if_interacted": interacted,
        "model_signals": ", ".join(s["matched_text"] for s in signals if s["matched_text"]) or "No configured warning phrases matched",
        "privacy": "This starter app processes the text locally in the Flask application; avoid pasting passwords, OTPs, or private personal information.",
        "risk_note": "The risk indicator is a simple educational heuristic based on the model label and detected warning signals. It is not a calibrated probability or a guarantee."
    }


@app.route("/")
def home():
    return render_template("index.html", page="home")


@app.route("/scanner")
def scanner():
    return render_template("scanner.html", page="scanner")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or request.form
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Please paste an email or message to scan."}), 400
    if len(text) > 20000:
        return jsonify({"error": "Please keep the message under 20,000 characters."}), 400
    try:
        return jsonify(predict_email(text))
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({"error": "The scan could not be completed. Please try again."}), 500


@app.route("/safety")
def safety():
    return render_template("safety.html", page="safety")


@app.route("/citizen-manual")
def citizen_manual():
    return render_template("citizen_manual.html", page="manual")


@app.route("/report")
def report():
    return render_template("report.html", page="report")


@app.route("/after-scam")
def after_scam():
    return render_template("after_scam.html", page="help")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "model": "loaded"})


if __name__ == "__main__":
    app.run(debug=False)
