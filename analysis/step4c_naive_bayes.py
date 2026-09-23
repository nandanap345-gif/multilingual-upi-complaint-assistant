import os
import json
import joblib
import numpy as np

from datetime import datetime, timezone

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# STEP 4C — MULTINOMIAL NAIVE BAYES
# TF-IDF + Multinomial Naive Bayes — BANKING77
# ============================================================

ROOT = os.path.dirname(os.path.dirname(__file__))

TRAIN_PATH = os.path.join(
    ROOT,
    "data",
    "processed",
    "banking77_train.csv"
)

TEST_PATH = os.path.join(
    ROOT,
    "data",
    "processed",
    "banking77_test.csv"
)

MODELS_DIR = os.path.join(ROOT, "models")
ANALYSIS_DIR = os.path.join(ROOT, "analysis")

MODEL_PATH = os.path.join(
    MODELS_DIR,
    "step4c_multinomial_nb.joblib"
)

VECTORIZER_PATH = os.path.join(
    MODELS_DIR,
    "step4c_tfidf_vectorizer.joblib"
)

RESULTS_PATH = os.path.join(
    ANALYSIS_DIR,
    "step4c_results.json"
)

REPORT_PATH = os.path.join(
    ANALYSIS_DIR,
    "STEP4C_NAIVE_BAYES_REPORT.md"
)


# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def load_csv(path):
    import csv

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def calculate_metrics(y_true, y_pred):
    return {
        "accuracy": float(
            accuracy_score(y_true, y_pred)
        ),

        "weighted_precision": float(
            precision_score(
                y_true,
                y_pred,
                average="weighted",
                zero_division=0
            )
        ),

        "weighted_recall": float(
            recall_score(
                y_true,
                y_pred,
                average="weighted",
                zero_division=0
            )
        ),

        "weighted_f1": float(
            f1_score(
                y_true,
                y_pred,
                average="weighted",
                zero_division=0
            )
        ),

        "macro_precision": float(
            precision_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0
            )
        ),

        "macro_recall": float(
            recall_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0
            )
        ),

        "macro_f1": float(
            f1_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0
            )
        )
    }


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print("=" * 70)
    print("STEP 4C — MULTINOMIAL NAIVE BAYES")
    print("TF-IDF + Multinomial Naive Bayes — BANKING77")
    print("=" * 70)

    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    # --------------------------------------------------------
    # 1. Load processed datasets
    # --------------------------------------------------------

    print("\n[1] Loading processed datasets...")

    train_rows = load_csv(TRAIN_PATH)
    test_rows = load_csv(TEST_PATH)

    print(f"Training rows : {len(train_rows)}")
    print(f"Testing rows  : {len(test_rows)}")

    # --------------------------------------------------------
    # 2. Extract text and labels
    # --------------------------------------------------------

    print("\n[2] Extracting text and intent labels...")

    X_train_text = [
        row["text"]
        for row in train_rows
    ]

    y_train = [
        row["category"]
        for row in train_rows
    ]

    X_test_text = [
        row["text"]
        for row in test_rows
    ]

    y_test = [
        row["category"]
        for row in test_rows
    ]

    train_classes = sorted(set(y_train))
    test_classes = sorted(set(y_test))
    combined_classes = sorted(
        set(y_train).union(set(y_test))
    )

    print(f"Training classes : {len(train_classes)}")
    print(f"Testing classes  : {len(test_classes)}")
    print(f"Combined classes : {len(combined_classes)}")

    if len(combined_classes) != 77:
        raise ValueError(
            f"Expected 77 BANKING77 intents, "
            f"found {len(combined_classes)}."
        )

    # --------------------------------------------------------
    # 3. TF-IDF representation
    # --------------------------------------------------------

    print("\n[3] Creating TF-IDF representation...")

    vectorizer = TfidfVectorizer(
        lowercase=False,
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )

    X_train_tfidf = vectorizer.fit_transform(
        X_train_text
    )

    X_test_tfidf = vectorizer.transform(
        X_test_text
    )

    vocabulary_size = len(
        vectorizer.vocabulary_
    )

    print(
        f"Training TF-IDF shape: "
        f"{X_train_tfidf.shape}"
    )

    print(
        f"Testing TF-IDF shape : "
        f"{X_test_tfidf.shape}"
    )

    print(
        f"Vocabulary size      : "
        f"{vocabulary_size}"
    )

    # --------------------------------------------------------
    # 4. Train Multinomial Naive Bayes
    # --------------------------------------------------------

    print("\n[4] Training Multinomial Naive Bayes...")

    model = MultinomialNB(
        alpha=0.1
    )

    model.fit(
        X_train_tfidf,
        y_train
    )

    print("Model training completed.")

    # --------------------------------------------------------
    # 5. Generate predictions
    # --------------------------------------------------------

    print("\n[5] Generating predictions...")

    y_pred = model.predict(
        X_test_tfidf
    )

    print("Prediction completed.")

    # --------------------------------------------------------
    # 6. Evaluate model
    # --------------------------------------------------------

    print("\n[6] Evaluating Multinomial Naive Bayes...")

    metrics = calculate_metrics(
        y_test,
        y_pred
    )

    print("\n" + "-" * 50)
    print("MULTINOMIAL NAIVE BAYES RESULTS")
    print("-" * 50)

    print(
        f"Accuracy           : "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Weighted Precision : "
        f"{metrics['weighted_precision']:.4f}"
    )

    print(
        f"Weighted Recall    : "
        f"{metrics['weighted_recall']:.4f}"
    )

    print(
        f"Weighted F1        : "
        f"{metrics['weighted_f1']:.4f}"
    )

    print(
        f"Macro Precision    : "
        f"{metrics['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall       : "
        f"{metrics['macro_recall']:.4f}"
    )

    print(
        f"Macro F1           : "
        f"{metrics['macro_f1']:.4f}"
    )

    # --------------------------------------------------------
    # 7. Save model
    # --------------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH
    )

    joblib.dump(
        vectorizer,
        VECTORIZER_PATH
    )

    print("\nModel saved to:")
    print(MODEL_PATH)

    print("\nVectorizer saved to:")
    print(VECTORIZER_PATH)

    # --------------------------------------------------------
    # 8. Save results JSON
    # --------------------------------------------------------

    results = {
        "step": "4C",
        "model": "Multinomial Naive Bayes",
        "representation": "TF-IDF",
        "dataset": "BANKING77",
        "training_rows": len(train_rows),
        "testing_rows": len(test_rows),
        "training_classes": len(train_classes),
        "testing_classes": len(test_classes),
        "combined_classes": len(combined_classes),
        "vocabulary_size": vocabulary_size,
        "tfidf_ngram_range": [1, 2],
        "lowercase": False,
        "sublinear_tf": True,
        "alpha": 0.1,
        "metrics": metrics,
        "model_artifact": MODEL_PATH,
        "vectorizer_artifact": VECTORIZER_PATH,
        "generated_on": datetime.now(
            timezone.utc
        ).isoformat()
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            results,
            f,
            indent=2
        )

    # --------------------------------------------------------
    # 9. Save report
    # --------------------------------------------------------

    report = f"""# STEP 4C — MULTINOMIAL NAIVE BAYES

## Objective

Train and evaluate a Multinomial Naive Bayes classifier for BANKING77 intent classification using TF-IDF text representations.

## Dataset

- Dataset: BANKING77
- Training rows: {len(train_rows)}
- Testing rows: {len(test_rows)}
- Number of intents: {len(combined_classes)}

## Text Representation

TF-IDF was used to convert customer-support text into numerical feature vectors.

Configuration:

- n-gram range: (1, 2)
- lowercase: False
- sublinear TF: True
- Vocabulary size: {vocabulary_size}

## Model

Multinomial Naive Bayes was used as a lightweight probabilistic text-classification model.

Hyperparameter:

- alpha: 0.1

## Evaluation Metrics

| Metric | Score |
|---|---:|
| Accuracy | {metrics['accuracy']:.6f} |
| Weighted Precision | {metrics['weighted_precision']:.6f} |
| Weighted Recall | {metrics['weighted_recall']:.6f} |
| Weighted F1 | {metrics['weighted_f1']:.6f} |
| Macro Precision | {metrics['macro_precision']:.6f} |
| Macro Recall | {metrics['macro_recall']:.6f} |
| Macro F1 | {metrics['macro_f1']:.6f} |

## Interpretation

The Multinomial Naive Bayes model provides a lightweight probabilistic baseline for comparison with the Logistic Regression and Linear SVM models developed in Steps 4A and 4B.

The model is evaluated on the same processed BANKING77 test set used by the other baseline models.

## Reproducibility

The trained model and TF-IDF vectorizer were saved as separate artifacts.

Model:
`{MODEL_PATH}`

Vectorizer:
`{VECTORIZER_PATH}`

## Modeling Scope

Only the processed BANKING77 dataset was used for this baseline model.

No raw dataset was modified.

Generated on:
`{results['generated_on']}`
"""

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(report)

    print("\nResults saved to:")
    print(RESULTS_PATH)

    print("\nReport saved to:")
    print(REPORT_PATH)

    print("\n" + "=" * 70)
    print("STEP 4C COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()