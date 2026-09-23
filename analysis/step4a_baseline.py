import os
import json
import csv
import random
import numpy as np

from datetime import datetime, timezone

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)


# ============================================================
# STEP 4A — BASELINE MODELING
# TF-IDF + Logistic Regression on BANKING77
# ============================================================

ROOT = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(ROOT, "data", "processed")
MODEL_DIR = os.path.join(ROOT, "models")
ANALYSIS_DIR = os.path.join(ROOT, "analysis")

TRAIN_PATH = os.path.join(DATA_DIR, "banking77_train.csv")
TEST_PATH = os.path.join(DATA_DIR, "banking77_test.csv")

RESULT_PATH = os.path.join(
    ANALYSIS_DIR,
    "step4a_results.json"
)

REPORT_PATH = os.path.join(
    ANALYSIS_DIR,
    "STEP4A_BASELINE_REPORT.md"
)


RANDOM_STATE = 42


# ============================================================
# Utility functions
# ============================================================

def fail(message):
    print("ERROR:", message)
    raise SystemExit(2)


def load_csv(path):
    if not os.path.exists(path):
        fail(f"Dataset not found: {path}")

    with open(path, "r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def ensure_directories():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("STEP 4A — BASELINE MODELING")
    print("TF-IDF + Logistic Regression — BANKING77")
    print("=" * 70)

    random.seed(RANDOM_STATE)
    np.random.seed(RANDOM_STATE)

    ensure_directories()

    # --------------------------------------------------------
    # 1. Load processed datasets
    # --------------------------------------------------------

    print("\n[1] Loading processed datasets...")

    train_rows = load_csv(TRAIN_PATH)
    test_rows = load_csv(TEST_PATH)

    print(f"Training rows : {len(train_rows)}")
    print(f"Testing rows  : {len(test_rows)}")

    if len(train_rows) == 0:
        fail("Training dataset is empty.")

    if len(test_rows) == 0:
        fail("Testing dataset is empty.")

    # --------------------------------------------------------
    # 2. Extract text and labels
    # --------------------------------------------------------

    print("\n[2] Extracting text and intent labels...")

    X_train = [
        row.get("text", "")
        for row in train_rows
    ]

    y_train = [
        row.get("category", "")
        for row in train_rows
    ]

    X_test = [
        row.get("text", "")
        for row in test_rows
    ]

    y_test = [
        row.get("category", "")
        for row in test_rows
    ]

    # --------------------------------------------------------
    # 3. Basic validation
    # --------------------------------------------------------

    if any(label == "" for label in y_train):
        fail("Empty labels found in training data.")

    if any(label == "" for label in y_test):
        fail("Empty labels found in testing data.")

    train_classes = set(y_train)
    test_classes = set(y_test)

    print(f"Training classes : {len(train_classes)}")
    print(f"Testing classes  : {len(test_classes)}")

    if len(train_classes) != 77:
        fail(
            f"Expected 77 training intents, "
            f"found {len(train_classes)}."
        )

    if len(test_classes) != 77:
        fail(
            f"Expected 77 testing intents, "
            f"found {len(test_classes)}."
        )

    # --------------------------------------------------------
    # 4. TF-IDF vectorization
    # --------------------------------------------------------

    print("\n[3] Creating TF-IDF representation...")

    vectorizer = TfidfVectorizer(
        lowercase=False,
        strip_accents=None,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True
    )

    # IMPORTANT:
    # Fit ONLY on training data.
    X_train_tfidf = vectorizer.fit_transform(X_train)

    # Transform test data using the training vocabulary.
    X_test_tfidf = vectorizer.transform(X_test)

    print(
        "Training TF-IDF shape:",
        X_train_tfidf.shape
    )

    print(
        "Testing TF-IDF shape :",
        X_test_tfidf.shape
    )

    print(
        "Vocabulary size      :",
        len(vectorizer.vocabulary_)
    )

    # --------------------------------------------------------
    # 5. Train Logistic Regression
    # --------------------------------------------------------

    print("\n[4] Training Logistic Regression...")

    base_model = LogisticRegression(
    max_iter=2000,
    random_state=RANDOM_STATE,
    solver="liblinear"
)

    model = OneVsRestClassifier(
    base_model
)
    

    model.fit(
        X_train_tfidf,
        y_train
    )

    print("Model training completed.")

    # --------------------------------------------------------
    # 6. Prediction
    # --------------------------------------------------------

    print("\n[5] Generating predictions...")

    y_pred = model.predict(X_test_tfidf)

    print("Prediction completed.")

    # --------------------------------------------------------
    # 7. Evaluation
    # --------------------------------------------------------

    print("\n[6] Evaluating baseline model...")

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    macro_precision = precision_score(
        y_test,
        y_pred,
        average="macro",
        zero_division=0
    )

    macro_recall = recall_score(
        y_test,
        y_pred,
        average="macro",
        zero_division=0
    )

    macro_f1 = f1_score(
        y_test,
        y_pred,
        average="macro",
        zero_division=0
    )

    print("\n" + "-" * 50)
    print("BASELINE RESULTS")
    print("-" * 50)

    print(f"Accuracy          : {accuracy:.4f}")
    print(f"Weighted Precision : {precision:.4f}")
    print(f"Weighted Recall    : {recall:.4f}")
    print(f"Weighted F1        : {f1:.4f}")
    print(f"Macro Precision    : {macro_precision:.4f}")
    print(f"Macro Recall       : {macro_recall:.4f}")
    print(f"Macro F1           : {macro_f1:.4f}")

    # --------------------------------------------------------
    # 8. Detailed classification report
    # --------------------------------------------------------

    report = classification_report(
        y_test,
        y_pred,
        zero_division=0,
        output_dict=True
    )

    # --------------------------------------------------------
    # 9. Save model
    # --------------------------------------------------------

    # Save model using joblib.
    import joblib

    model_path = os.path.join(
        MODEL_DIR,
        "step4a_tfidf_logistic_regression.joblib"
    )

    vectorizer_path = os.path.join(
        MODEL_DIR,
        "step4a_tfidf_vectorizer.joblib"
    )

    joblib.dump(
        model,
        model_path
    )

    joblib.dump(
        vectorizer,
        vectorizer_path
    )

    print("\nModel saved to:")
    print(model_path)

    print("\nVectorizer saved to:")
    print(vectorizer_path)

    # --------------------------------------------------------
    # 10. Save results JSON
    # --------------------------------------------------------

    results = {
        "step": "4A",
        "experiment": "TF-IDF + Logistic Regression",
        "dataset": "BANKING77",
        "random_state": RANDOM_STATE,

        "training_rows": len(train_rows),
        "testing_rows": len(test_rows),

        "training_classes": len(train_classes),
        "testing_classes": len(test_classes),

        "tfidf": {
            "ngram_range": [1, 2],
            "lowercase": False,
            "strip_accents": None,
            "sublinear_tf": True,
            "max_df": 0.95,
            "min_df": 1,
            "vocabulary_size": len(
                vectorizer.vocabulary_
            ),
            "train_matrix_shape": list(
                X_train_tfidf.shape
            ),
            "test_matrix_shape": list(
                X_test_tfidf.shape
            )
        },

        "model": {
            "algorithm": "One-vs-Rest Logistic Regression",
            "base_estimator": "Logistic Regression",
            "solver": "liblinear",
            "max_iter": 2000,
            "number_of_classes": 77
        },  

        "metrics": {
            "accuracy": float(accuracy),
            "weighted_precision": float(precision),
            "weighted_recall": float(recall),
            "weighted_f1": float(f1),
            "macro_precision": float(macro_precision),
            "macro_recall": float(macro_recall),
            "macro_f1": float(macro_f1)
        },

        "classification_report": report,

        "model_path": os.path.relpath(
            model_path,
            ROOT
        ),

        "vectorizer_path": os.path.relpath(
            vectorizer_path,
            ROOT
        ),

        "generated_on": datetime.now(
            timezone.utc
        ).isoformat(),

        "preprocessing_note": (
            "Processed data from Step 3G was used. "
            "No additional translation, transliteration, "
            "or synthetic Malayalam data was introduced."
        )
    }

    with open(
        RESULT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2
        )

    # --------------------------------------------------------
    # 11. Generate Markdown report
    # --------------------------------------------------------

    report_text = f"""# STEP 4A — BASELINE MODELING REPORT

## Objective

Establish a reproducible classical NLP baseline for BANKING77
intent classification before evaluating stronger machine-learning
and multilingual transformer approaches.

## Dataset

- Dataset: BANKING77
- Training rows: {len(train_rows)}
- Testing rows: {len(test_rows)}
- Number of intents: 77

## Input and target

- Input feature: `text`
- Target label: `category`

## Feature Representation

TF-IDF was used with:

- n-gram range: (1, 2)
- lowercase: False
- accent stripping: None
- sublinear TF: True
- minimum document frequency: 1
- maximum document frequency: 0.95

Vocabulary size:

- {len(vectorizer.vocabulary_)}

Training matrix:

- {X_train_tfidf.shape}

Testing matrix:

- {X_test_tfidf.shape}

## Model

One-vs-Rest Logistic Regression was used as the first classical
baseline.

A Logistic Regression classifier with the liblinear solver was
wrapped using OneVsRestClassifier to explicitly support the
77-class classification problem.

Parameters:

- base classifier: Logistic Regression
- solver: liblinear
- max_iter: 2000
- multi-class strategy: One-vs-Rest
- random_state: 42

## Results

| Metric | Score |
|---|---:|
| Accuracy | {accuracy:.4f} |
| Weighted Precision | {precision:.4f} |
| Weighted Recall | {recall:.4f} |
| Weighted F1 | {f1:.4f} |
| Macro Precision | {macro_precision:.4f} |
| Macro Recall | {macro_recall:.4f} |
| Macro F1 | {macro_f1:.4f} |

## Methodological Notes

TF-IDF was fitted only on the training data. The test data was
transformed using the vocabulary learned from the training data.

The processed datasets generated during Step 3G were used without
modifying the raw datasets.

No translation, transliteration, synthetic Malayalam generation,
or external multilingual augmentation was introduced during this
baseline experiment.

## Purpose of this baseline

This experiment provides a classical NLP reference point against
which later models can be compared.

Later experiments should use the same test set and evaluation
protocol wherever methodologically appropriate.

## Saved Artifacts

- Model: `models/step4a_tfidf_logistic_regression.joblib`
- Vectorizer: `models/step4a_tfidf_vectorizer.joblib`
- Results: `analysis/step4a_results.json`

## Status

STEP 4A BASELINE MODELING COMPLETED.
"""

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report_text)

    print("\n" + "=" * 70)
    print("STEP 4A COMPLETED")
    print("=" * 70)

    print(f"Results : {RESULT_PATH}")
    print(f"Report  : {REPORT_PATH}")


if __name__ == "__main__":
    main()