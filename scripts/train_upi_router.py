from __future__ import annotations

import csv
import json
import os
import random
from collections import Counter
from itertools import product

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_PATH = os.path.join(ROOT, "data", "raw", "seed_dataset.csv")
OUTPUT_PATH = os.path.join(ROOT, "data", "processed", "upi_router_augmented_train.csv")
MODEL_PATH = os.path.join(ROOT, "models", "upi_router_char_logreg.joblib")
REPORT_PATH = os.path.join(ROOT, "analysis", "upi_router_training_report.json")


INTENT_CORE_PHRASES = {
    "PAYMENT_FAILED": [
        "പേയ്മെന്റ് പരാജയപ്പെട്ടു",
        "ട്രാൻസാക്ഷൻ ഫെയിൽ ആയി",
        "UPI payment failed ആണ്",
        "പണം അയക്കാൻ ശ്രമിച്ചപ്പോൾ failure ആയി",
    ],
    "MONEY_DEDUCTED_PAYMENT_FAILED": [
        "പണം ഡെബിറ്റ് ആയി പക്ഷേ പേയ്മെന്റ് പരാജയപ്പെട്ടു",
        "ട്രാൻസാക്ഷൻ fail ആയി പക്ഷേ amount പോയി",
        "പണം പോയി എന്നാൽ payment വിജയിച്ചില്ല",
        "money was deducted but payment failed",
    ],
    "PAYMENT_PENDING": [
        "പേയ്മെന്റ് പെൻഡിങ് ആണ്",
        "ട്രാൻസാക്ഷൻ ഇപ്പോഴും pending ആണ്",
        "പണം പോയി പക്ഷേ സ്റ്റാറ്റസ് pending ആയി കാണിക്കുന്നു",
        "payment status മാറുന്നില്ല",
    ],
    "MONEY_DEDUCTED_NO_RECIPIENT": [
        "പണം ട്രാൻസ്ഫർ ചെയ്തു പക്ഷേ കിട്ടിയില്ല",
        "beneficiaryക്ക് പണം ലഭിച്ചില്ല",
        "പണം പോയി പക്ഷേ മറ്റേ അക്കൗണ്ടിൽ എത്തിയില്ല",
        "transfer successful ആണെങ്കിലും സ്വീകരിച്ചില്ല",
    ],
    "WRONG_AMOUNT": [
        "തെറ്റായ തുക പോയി",
        "requested amount അല്ലാതെ വേറെ amount debit ആയി",
        "അധിക തുക transfer ആയി",
        "less amount went through",
    ],
    "DUPLICATE_TRANSACTION": [
        "രണ്ട് പ്രാവശ്യം പണം പോയി",
        "duplicate transaction ആണ്",
        "same payment രണ്ടുതവണ debit ആയി",
        "അതേ ട്രാൻസാക്ഷൻ വീണ്ടും പോയി",
    ],
    "REFUND_NOT_RECEIVED": [
        "റിഫണ്ട് വന്നില്ല",
        "പണം തിരികെ കിട്ടിയില്ല",
        "refund pending ആണ്",
        "merchant refund ചെയ്തിട്ടും amount ലഭിച്ചില്ല",
    ],
    "FRAUD_OR_UNAUTHORIZED_TRANSACTION": [
        "ഞാൻ ചെയ്തതല്ല ഈ ട്രാൻസാക്ഷൻ",
        "അനധികൃത debit കാണിക്കുന്നു",
        "someone else used my UPI",
        "ഫ്രോഡ് ആയി തോന്നുന്നു",
    ],
    "QR_PAYMENT_PROBLEM": [
        "QR scan ചെയ്യുമ്പോൾ പേയ്മെന്റ് fail ആയി",
        "QR code പ്രവർത്തിക്കുന്നില്ല",
        "merchant QR invalid ആണ്",
        "scan ചെയ്തിട്ടും payment പോയില്ല",
    ],
    "UPI_PIN_OR_AUTHENTICATION_PROBLEM": [
        "UPI PIN ശരിയാകുന്നില്ല",
        "authentication failed ആണ്",
        "OTP വരുന്നില്ല",
        "PIN verify ആകുന്നില്ല",
    ],
    "BANK_ACCOUNT_LINKING_PROBLEM": [
        "ബാങ്ക് അക്കൗണ്ട് link ആകുന്നില്ല",
        "account UPIയിൽ കാണുന്നില്ല",
        "SMS permission issue ആണ്",
        "bank linking failed",
    ],
    "UPI_APP_TECHNICAL_PROBLEM": [
        "app തുറക്കുമ്പോൾ crash ആയി",
        "server error കാണിക്കുന്നു",
        "network പ്രശ്നം കാരണം പേയ്മെന്റ് fail ആയി",
        "UPI app പ്രവർത്തിക്കുന്നില്ല",
    ],
    "OTHER_UPI_COMPLAINT": [
        "കൂടുതൽ വിശദാംശങ്ങൾ വേണം",
        "issue വ്യക്തമല്ല",
        "what happened not clear",
        "ശരി ആയി മനസ്സിലായില്ല",
    ],
}

PREFIXES = ["", "ഞാൻ ", "എന്റെ അക്കൗണ്ടിൽ നിന്ന് "]
SUFFIXES = ["", " ദയവായി സഹായിക്കൂ", " ഇപ്പോൾ എന്ത് ചെയ്യണം?"]


def load_seed_rows():
    rows = []
    with open(SEED_PATH, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(row)
    return rows


def build_augmented_examples():
    rows = load_seed_rows()
    examples = []
    dedupe = set()

    def add_example(text: str, intent: str, language: str, script: str, source_type: str, source_id: str):
        cleaned = " ".join(text.split()).strip()
        key = (cleaned.lower(), intent)
        if cleaned and key not in dedupe:
            dedupe.add(key)
            examples.append(
                {
                    "text": cleaned,
                    "intent": intent,
                    "language": language,
                    "script": script,
                    "source_type": source_type,
                    "source_id": source_id,
                }
            )

    for row in rows:
        intent = row["intent"].strip()
        base_text = row["complaint_text"].strip()
        language = row.get("language", "English").strip() or "English"
        script = row.get("script", "Latin").strip() or "Latin"
        add_example(base_text, intent, language, script, "REAL", row.get("complaint_id", base_text))

    for intent, phrases in INTENT_CORE_PHRASES.items():
        for phrase_index, phrase in enumerate(phrases, start=1):
            for prefix, suffix in product(PREFIXES, SUFFIXES):
                text = f"{prefix}{phrase}{suffix}"
                if intent == "OTHER_UPI_COMPLAINT":
                    language, script = "English", "Latin"
                elif any(ch >= "\u0D00" and ch <= "\u0D7F" for ch in text):
                    language, script = "Malayalam", "Malayalam"
                else:
                    language, script = "English", "Latin"
                add_example(
                    text,
                    intent,
                    language,
                    script,
                    "AUGMENTED",
                    f"{intent}_{phrase_index:02d}",
                )

    for intent, phrases in EXTRA_INTENT_PHRASES.items():
        for phrase_index, phrase in enumerate(phrases, start=1):
            for prefix, suffix in product(PREFIXES, SUFFIXES):
                text = f"{prefix}{phrase}{suffix}"
                if any(ch >= "\u0D00" and ch <= "\u0D7F" for ch in text):
                    language, script = "Malayalam", "Malayalam"
                else:
                    language, script = "English", "Latin"
                add_example(
                    text,
                    intent,
                    language,
                    script,
                    "AUGMENTED",
                    f"{intent}_extra_{phrase_index:02d}",
                )

    random.Random(42).shuffle(examples)
    return examples


def save_augmented_dataset(examples):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["text", "intent", "language", "script", "source_type", "source_id"],
        )
        writer.writeheader()
        for row in examples:
            writer.writerow(row)


def train_model(examples):
    texts = [row["text"] for row in examples]
    labels = [row["intent"] for row in examples]

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    pipeline = Pipeline(
        steps=[
            (
                "vectorizer",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 6),
                    min_df=1,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=5000,
                    class_weight="balanced",
                    solver="lbfgs",
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    report = {
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "labels": len(sorted(set(labels))),
        "macro_f1": f1_score(y_test, predictions, average="macro"),
        "accuracy": accuracy_score(y_test, predictions),
        "class_distribution": dict(Counter(labels)),
        "classification_report": classification_report(y_test, predictions, zero_division=0, output_dict=True),
        "model_path": MODEL_PATH,
        "dataset_path": OUTPUT_PATH,
    }

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    return report


EXTRA_INTENT_PHRASES = {
    "PAYMENT_PENDING": [
        "ഞാൻ ഓൺലൈനിൽ പേയ്മെൻറ് നടത്തി പക്ഷേ പേയ്മെൻറ് പെൻഡിങ് എന്നാണ് കാണിക്കുന്നത്",
        "അക്കൗണ്ടിൽ നിന്ന് പൈസ പോയി പക്ഷേ പേയ്മെൻറ് പെൻഡിങ് ആണ്",
        "പേയ്മെൻറ് പെൻഡിങ് ആയി കാണുന്നു, പണം പോയിട്ടുണ്ട്",
        "status pending ആണ്, amount debit ആയി",
    ],
    "MONEY_DEDUCTED_PAYMENT_FAILED": [
        "പണം ഡെബിറ്റ് ആയി പക്ഷേ പേയ്മെൻറ് ഫെയിൽ ആയി",
        "payment failed but money debited ആണെന്ന് കാണിക്കുന്നു",
        "ട്രാൻസാക്ഷൻ failed ആണ് പക്ഷേ amount പോയി",
    ],
    "MONEY_DEDUCTED_NO_RECIPIENT": [
        "പണം ട്രാൻസ്ഫർ ചെയ്തു പക്ഷേ അവിടെ എത്തിയില്ല",
        "ട്രാൻസ്ഫർ വിജയിച്ചു പക്ഷേ beneficiaryക്ക് ലഭിച്ചില്ല",
    ],
    "REFUND_NOT_RECEIVED": [
        "റിഫണ്ട് വന്നില്ല",
        "പണം തിരികെ കിട്ടിയില്ല",
        "refund pending ആയി തന്നെ ഇരിക്കുന്നു",
    ],
}


def main():
    examples = build_augmented_examples()
    save_augmented_dataset(examples)
    report = train_model(examples)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
