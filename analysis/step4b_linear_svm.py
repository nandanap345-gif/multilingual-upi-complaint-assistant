import os
import csv
import json
import joblib
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# PATHS
# ============================================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRAIN_PATH = os.path.join(
    ROOT, "data", "processed", "banking77_train.csv"
)

TEST_PATH = os.path.join(
    ROOT, "data", "processed", "banking77_test.csv"
)

MODEL_DIR = os.path.join(ROOT, "models")
ANALYSIS_DIR = os.path.join(ROOT, "analysis")

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "step4b_linear_svm.joblib"
)

VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "step4b_tfidf_vectorizer.joblib"
)

RESULTS_PATH = os.path.join(
    ANALYSIS_DIR,
    "step4b_results.json"
)

REPORT_PATH = os.path.join(
    ANALYSIS_DIR,
    "STEP4B_LINEAR_SVM_REPORT.md"
)

CONFUSION_MATRIX_PATH = os.path.join(
    ANALYSIS_DIR,
    "step4b_confusion_matrix.npy"
)


# ============================================================
# LOAD CSV
# ============================================================

def load_dataset(path):

    texts = []
    labels = []

    with open(
        path,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        if "text" not in reader.fieldnames:
            raise ValueError(
                f"'text' column missing in {path}"
            )

        if "category" not in reader.fieldnames:
            raise ValueError(
                f"'category' column missing in {path}"
            )

        for row in reader:
            texts.append(row["text"])
            labels.append(row["category"])

    return texts, labels


# ============================================================
# SAVE JSON
# ============================================================

def save_json(data, path):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("STEP 4B — LINEAR SVM BASELINE")
    print("TF-IDF + Linear Support Vector Machine — BANKING77")
    print("=" * 70)

    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    # --------------------------------------------------------
    # 1. Load datasets
    # --------------------------------------------------------

    print("\n[1] Loading processed datasets...")

    X_train_text, y_train = load_dataset(TRAIN_PATH)
    X_test_text, y_test = load_dataset(TEST_PATH)

    print("Training rows :", len(X_train_text))
    print("Testing rows  :", len(X_test_text))

    # --------------------------------------------------------
    # 2. Check classes
    # --------------------------------------------------------

    print("\n[2] Checking intent classes...")

    train_classes = sorted(set(y_train))
    test_classes = sorted(set(y_test))
    combined_classes = sorted(
        set(train_classes).union(test_classes)
    )

    print("Training classes :", len(train_classes))
    print("Testing classes  :", len(test_classes))
    print("Combined classes :", len(combined_classes))

    if len(combined_classes) != 77:
        raise ValueError(
            "BANKING77 should contain exactly 77 intents."
        )

    # --------------------------------------------------------
    # 3. TF-IDF
    # --------------------------------------------------------

    print("\n[3] Creating TF-IDF representation...")

    vectorizer = TfidfVectorizer(
        lowercase=False,
        strip_accents=None,
        ngram_range=(1, 2),
        min_df=1,
        max_df=1.0,
        sublinear_tf=True
    )

    # IMPORTANT:
    # Fit ONLY on training data.
    X_train_tfidf = vectorizer.fit_transform(
        X_train_text
    )

    # Transform test using training vocabulary.
    X_test_tfidf = vectorizer.transform(
        X_test_text
    )

    vocabulary_size = len(
        vectorizer.vocabulary_
    )

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
        vocabulary_size
    )

    # --------------------------------------------------------
    # 4. Train Linear SVM
    # --------------------------------------------------------

    print("\n[4] Training Linear SVM...")

    model = LinearSVC(
        C=1.0,
        max_iter=5000,
        random_state=42
    )

    model.fit(
        X_train_tfidf,
        y_train
    )

    print("Model training completed.")

    # --------------------------------------------------------
    # 5. Predictions
    # --------------------------------------------------------

    print("\n[5] Generating predictions...")

    y_pred = model.predict(
        X_test_tfidf
    )

    print("Prediction completed.")

    # --------------------------------------------------------
    # 6. Evaluation
    # --------------------------------------------------------

    print("\n[6] Evaluating Linear SVM...")

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    weighted_precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    weighted_recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    weighted_f1 = f1_score(
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
    print("LINEAR SVM RESULTS")
    print("-" * 50)

    print(f"Accuracy           : {accuracy:.4f}")
    print(f"Weighted Precision : {weighted_precision:.4f}")
    print(f"Weighted Recall    : {weighted_recall:.4f}")
    print(f"Weighted F1        : {weighted_f1:.4f}")
    print(f"Macro Precision    : {macro_precision:.4f}")
    print(f"Macro Recall       : {macro_recall:.4f}")
    print(f"Macro F1           : {macro_f1:.4f}")

    # --------------------------------------------------------
    # 7. Classification report
    # --------------------------------------------------------

    class_report = classification_report(
        y_test,
        y_pred,
        zero_division=0
    )

    # --------------------------------------------------------
    # 8. Confusion matrix
    # --------------------------------------------------------

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=model.classes_
    )

    np.save(
        CONFUSION_MATRIX_PATH,
        cm
    )

    print("\nConfusion matrix saved to:")
    print(CONFUSION_MATRIX_PATH)

    # --------------------------------------------------------
    # 9. Save model
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
    # 10. Save results JSON
    # --------------------------------------------------------

    results = {
        "step": "4B",
        "model": "LinearSVC",
        "representation": "TF-IDF",
        "dataset": "BANKING77",

        "training_rows": len(X_train_text),
        "testing_rows": len(X_test_text),

        "training_classes": len(train_classes),
        "testing_classes": len(test_classes),
        "combined_classes": len(combined_classes),

        "vocabulary_size": vocabulary_size,

        "tfidf_training_shape": [
            X_train_tfidf.shape[0],
            X_train_tfidf.shape[1]
        ],

        "tfidf_testing_shape": [
            X_test_tfidf.shape[0],
            X_test_tfidf.shape[1]
        ],

        "hyperparameters": {
            "C": 1.0,
            "max_iter": 5000,
            "random_state": 42
        },

        "metrics": {
            "accuracy": float(accuracy),
            "weighted_precision": float(
                weighted_precision
            ),
            "weighted_recall": float(
                weighted_recall
            ),
            "weighted_f1": float(
                weighted_f1
            ),
            "macro_precision": float(
                macro_precision
            ),
            "macro_recall": float(
                macro_recall
            ),
            "macro_f1": float(
                macro_f1
            )
        },

        "classification_report": class_report,

        "confusion_matrix_shape": [
            cm.shape[0],
            cm.shape[1]
        ],

        "confusion_matrix_path": CONFUSION_MATRIX_PATH
    }

    save_json(
        results,
        RESULTS_PATH
    )

    # --------------------------------------------------------
    # 11. Create Markdown report
    # --------------------------------------------------------

    report_lines = []

    report_lines.append(
        "# STEP 4B — Linear SVM Baseline"
    )

    report_lines.append("")

    report_lines.append("## 1. Objective")
    report_lines.append("")
    report_lines.append(
        "Step 4B establishes a classical Linear "
        "Support Vector Machine baseline for "
        "BANKING77 intent classification using "
        "TF-IDF text representation."
    )

    report_lines.append("")

    report_lines.append("## 2. Dataset")
    report_lines.append("")
    report_lines.append(
        "- Dataset: BANKING77"
    )
    report_lines.append(
        f"- Training records: {len(X_train_text)}"
    )
    report_lines.append(
        f"- Testing records: {len(X_test_text)}"
    )
    report_lines.append(
        f"- Intent classes: {len(combined_classes)}"
    )
    report_lines.append(
        "- Original train/test separation preserved."
    )

    report_lines.append("")

    report_lines.append("## 3. TF-IDF Representation")
    report_lines.append("")
    report_lines.append(
        "- Lowercasing: disabled"
    )
    report_lines.append(
        "- Accent stripping: disabled"
    )
    report_lines.append(
        "- N-gram range: (1, 2)"
    )
    report_lines.append(
        "- Sublinear TF: enabled"
    )
    report_lines.append(
        "- Minimum document frequency: 1"
    )
    report_lines.append(
        "- Maximum document frequency: 1.0"
    )
    report_lines.append(
        f"- Vocabulary size: {vocabulary_size}"
    )
    report_lines.append(
        f"- Training TF-IDF shape: {X_train_tfidf.shape}"
    )
    report_lines.append(
        f"- Testing TF-IDF shape: {X_test_tfidf.shape}"
    )

    report_lines.append("")

    report_lines.append("## 4. Linear SVM Configuration")
    report_lines.append("")
    report_lines.append(
        "- Model: LinearSVC"
    )
    report_lines.append(
        "- C: 1.0"
    )
    report_lines.append(
        "- max_iter: 5000"
    )
    report_lines.append(
        "- random_state: 42"
    )

    report_lines.append("")

    report_lines.append("## 5. Evaluation Results")
    report_lines.append("")
    report_lines.append("| Metric | Score |")
    report_lines.append("|---|---:|")
    report_lines.append(
        f"| Accuracy | {accuracy:.4f} |"
    )
    report_lines.append(
        f"| Weighted Precision | {weighted_precision:.4f} |"
    )
    report_lines.append(
        f"| Weighted Recall | {weighted_recall:.4f} |"
    )
    report_lines.append(
        f"| Weighted F1 | {weighted_f1:.4f} |"
    )
    report_lines.append(
        f"| Macro Precision | {macro_precision:.4f} |"
    )
    report_lines.append(
        f"| Macro Recall | {macro_recall:.4f} |"
    )
    report_lines.append(
        f"| Macro F1 | {macro_f1:.4f} |"
    )

    report_lines.append("")

    report_lines.append("## 6. Leakage Prevention")
    report_lines.append("")
    report_lines.append(
        "The TF-IDF vectorizer was fitted exclusively "
        "on the training data. The test data was "
        "transformed using the fitted training "
        "vectorizer. No test data was used during "
        "training or vocabulary construction."
    )

    report_lines.append("")

    report_lines.append("## 7. Comparison with Step 4A")
    report_lines.append("")
    report_lines.append(
        "Step 4A used TF-IDF with One-vs-Rest Logistic "
        "Regression. Step 4B uses TF-IDF with Linear "
        "SVM. Both models use the same processed "
        "BANKING77 train/test data so that their "
        "performance can be compared fairly."
    )

    report_lines.append("")

    report_lines.append("## 8. Model Artifacts")
    report_lines.append("")
    report_lines.append(
        f"- Model: `{MODEL_PATH}`"
    )
    report_lines.append(
        f"- Vectorizer: `{VECTORIZER_PATH}`"
    )
    report_lines.append(
        f"- Results: `{RESULTS_PATH}`"
    )
    report_lines.append(
        f"- Confusion matrix: `{CONFUSION_MATRIX_PATH}`"
    )

    report_lines.append("")

    report_lines.append("## 9. Classification Report")
    report_lines.append("")
    report_lines.append("```text")
    report_lines.append(class_report)
    report_lines.append("```")

    report_lines.append("")

    report_lines.append("## 10. Conclusion")
    report_lines.append("")
    report_lines.append(
        "Step 4B establishes the Linear SVM baseline "
        "for BANKING77 intent classification. Its "
        "performance can be compared with the Step 4A "
        "Logistic Regression baseline before proceeding "
        "to subsequent modeling stages."
    )

    report = "\n".join(report_lines)

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
    print("STEP 4B COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()