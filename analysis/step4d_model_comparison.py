import os
import json
import csv


ROOT = os.path.dirname(os.path.dirname(__file__))

ANALYSIS = os.path.join(ROOT, "analysis")


# ------------------------------------------------------------
# Existing Step 4 result files
# ------------------------------------------------------------

RESULT_FILES = {
    "Logistic Regression": os.path.join(
        ANALYSIS,
        "step4a_results.json"
    ),
    "Linear SVM": os.path.join(
        ANALYSIS,
        "step4b_results.json"
    ),
    "Multinomial Naive Bayes": os.path.join(
        ANALYSIS,
        "step4c_results.json"
    )
}


OUTPUT_JSON = os.path.join(
    ANALYSIS,
    "step4d_model_comparison_results.json"
)

OUTPUT_REPORT = os.path.join(
    ANALYSIS,
    "STEP4D_MODEL_COMPARISON_REPORT.md"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def fail(message):
    print("ERROR:", message)
    raise SystemExit(2)


def load_json(path):
    if not os.path.exists(path):
        fail(f"Required results file missing: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def find_metric(data, possible_names):
    """
    Finds a metric even if the previous step used slightly
    different naming.
    """

    # Direct lookup
    for name in possible_names:
        if name in data:
            return float(data[name])

    # Search nested dictionaries
    for value in data.values():

        if isinstance(value, dict):

            for name in possible_names:
                if name in value:
                    return float(value[name])

    return None


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print("=" * 70)
    print("STEP 4D — CLASSICAL NLP MODEL COMPARISON")
    print("BANKING77")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Load results
    # --------------------------------------------------------

    print("\n[1] Loading existing Step 4 results...")

    results = {}

    for model_name, path in RESULT_FILES.items():

        data = load_json(path)

        accuracy = find_metric(
            data,
            [
                "accuracy",
                "Accuracy"
            ]
        )

        weighted_precision = find_metric(
            data,
            [
                "weighted_precision",
                "Weighted Precision",
                "weighted_precision_score"
            ]
        )

        weighted_recall = find_metric(
            data,
            [
                "weighted_recall",
                "Weighted Recall",
                "weighted_recall_score"
            ]
        )

        weighted_f1 = find_metric(
            data,
            [
                "weighted_f1",
                "Weighted F1",
                "weighted_f1_score"
            ]
        )

        macro_precision = find_metric(
            data,
            [
                "macro_precision",
                "Macro Precision",
                "macro_precision_score"
            ]
        )

        macro_recall = find_metric(
            data,
            [
                "macro_recall",
                "Macro Recall",
                "macro_recall_score"
            ]
        )

        macro_f1 = find_metric(
            data,
            [
                "macro_f1",
                "Macro F1",
                "macro_f1_score"
            ]
        )

        required = {
            "accuracy": accuracy,
            "weighted_precision": weighted_precision,
            "weighted_recall": weighted_recall,
            "weighted_f1": weighted_f1,
            "macro_precision": macro_precision,
            "macro_recall": macro_recall,
            "macro_f1": macro_f1
        }

        missing = [
            key
            for key, value in required.items()
            if value is None
        ]

        if missing:
            fail(
                f"{model_name}: missing metrics: {missing}"
            )

        results[model_name] = required

        print(f"PASS: {model_name} results loaded.")

    # --------------------------------------------------------
    # 2. Compare models
    # --------------------------------------------------------

    print("\n[2] Comparing classical NLP models...")

    best_model = max(
        results,
        key=lambda model: results[model]["macro_f1"]
    )

    print(
        "\nBest classical model:",
        best_model
    )

    print(
        "Selection criterion: highest Macro F1"
    )

    # --------------------------------------------------------
    # 3. Display comparison
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("CLASSICAL NLP MODEL COMPARISON")
    print("-" * 70)

    print(
        f"{'Model':30}"
        f"{'Accuracy':12}"
        f"{'Weighted F1':15}"
        f"{'Macro F1':12}"
    )

    print("-" * 70)

    for model_name, metrics in results.items():

        print(
            f"{model_name:30}"
            f"{metrics['accuracy']:.4f}      "
            f"{metrics['weighted_f1']:.4f}         "
            f"{metrics['macro_f1']:.4f}"
        )

    # --------------------------------------------------------
    # 4. Create comparison JSON
    # --------------------------------------------------------

    comparison_json = {
        "step": "4D",
        "dataset": "BANKING77",
        "models_compared": list(results.keys()),
        "selection_criterion": "Highest Macro F1",
        "best_classical_model": best_model,
        "results": results
    }

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as fh:

        json.dump(
            comparison_json,
            fh,
            indent=2
        )

    print(
        "\nComparison results saved to:"
    )
    print(OUTPUT_JSON)

    # --------------------------------------------------------
    # 5. Create report
    # --------------------------------------------------------

    print("\n[3] Creating Step 4D report...")

    report = f"""# STEP 4D — CLASSICAL NLP MODEL COMPARISON

## Objective

Step 4D compares the three classical NLP models implemented in
Steps 4A–4C on the BANKING77 intent-classification task.

No new machine-learning model was trained in Step 4D.

The purpose of this step is to identify the strongest classical
NLP baseline for comparison with the multilingual Transformer
model in the next stage of the project.

---

## Models Compared

1. TF-IDF + One-vs-Rest Logistic Regression
2. TF-IDF + Linear SVM
3. TF-IDF + Multinomial Naive Bayes

All three models use TF-IDF text representations and are evaluated
on the same processed BANKING77 test set.

---

## Evaluation Metrics

The following metrics are compared:

- Accuracy
- Weighted Precision
- Weighted Recall
- Weighted F1
- Macro Precision
- Macro Recall
- Macro F1

Macro F1 is used as the primary selection criterion because
BANKING77 contains 77 intent classes and Macro F1 gives equal
importance to every class.

---

## Results

| Model | Accuracy | Weighted Precision | Weighted Recall | Weighted F1 | Macro Precision | Macro Recall | Macro F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| TF-IDF + Logistic Regression | {results["Logistic Regression"]["accuracy"]:.4f} | {results["Logistic Regression"]["weighted_precision"]:.4f} | {results["Logistic Regression"]["weighted_recall"]:.4f} | {results["Logistic Regression"]["weighted_f1"]:.4f} | {results["Logistic Regression"]["macro_precision"]:.4f} | {results["Logistic Regression"]["macro_recall"]:.4f} | {results["Logistic Regression"]["macro_f1"]:.4f} |
| TF-IDF + Linear SVM | {results["Linear SVM"]["accuracy"]:.4f} | {results["Linear SVM"]["weighted_precision"]:.4f} | {results["Linear SVM"]["weighted_recall"]:.4f} | {results["Linear SVM"]["weighted_f1"]:.4f} | {results["Linear SVM"]["macro_precision"]:.4f} | {results["Linear SVM"]["macro_recall"]:.4f} | {results["Linear SVM"]["macro_f1"]:.4f} |
| TF-IDF + Multinomial Naive Bayes | {results["Multinomial Naive Bayes"]["accuracy"]:.4f} | {results["Multinomial Naive Bayes"]["weighted_precision"]:.4f} | {results["Multinomial Naive Bayes"]["weighted_recall"]:.4f} | {results["Multinomial Naive Bayes"]["weighted_f1"]:.4f} | {results["Multinomial Naive Bayes"]["macro_precision"]:.4f} | {results["Multinomial Naive Bayes"]["macro_recall"]:.4f} | {results["Multinomial Naive Bayes"]["macro_f1"]:.4f} |

---

## Best Classical NLP Model

**{best_model}** is selected as the strongest classical NLP
baseline because it achieved the highest Macro F1 score.

Its Macro F1 score is:

**{results[best_model]["macro_f1"]:.4f}**

Its accuracy is:

**{results[best_model]["accuracy"]:.4f}**

---

## Interpretation

The comparison demonstrates the performance of traditional
lexical NLP representations using TF-IDF.

TF-IDF represents text using weighted word and n-gram features.
The classifiers then learn relationships between these lexical
features and the 77 BANKING77 intent categories.

The results show that the Linear SVM provides the strongest
classical baseline among the three evaluated approaches.

This classical baseline will be used as a reference point for the
next stage, where a multilingual Transformer model will be
introduced.

---

## Transition to Multilingual NLP

The classical models primarily depend on lexical TF-IDF features.
They do not explicitly model contextual multilingual
representations.

Therefore, the next stage of the project moves from classical
feature-based NLP to multilingual Transformer-based NLP.

The selected direction is XLM-RoBERTa, which provides contextual
subword representations and multilingual transfer capabilities.

The objective is to determine whether a multilingual Transformer
can improve intent classification and provide better handling of
multilingual and code-mixed text.

---

## Scope

Step 4D only compares the existing models from Steps 4A–4C.

No new model was trained.

No raw dataset was modified.

No additional preprocessing was performed.
"""

    with open(
        OUTPUT_REPORT,
        "w",
        encoding="utf-8"
    ) as fh:

        fh.write(report)

    print(
        "Report saved to:"
    )
    print(OUTPUT_REPORT)

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("STEP 4D COMPLETED")
    print("=" * 70)

    print(
        "\nBest classical NLP model:",
        best_model
    )

    print(
        f"Accuracy : "
        f"{results[best_model]['accuracy']:.4f}"
    )

    print(
        f"Macro F1 : "
        f"{results[best_model]['macro_f1']:.4f}"
    )

    print("\nNo new model was trained.")
    print("No raw datasets were modified.")
    print("=" * 70)


if __name__ == "__main__":
    main()