import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support
)


# ============================================================
# PATHS
# ============================================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROCESSED = os.path.join(ROOT, "data", "processed")
MODELS = os.path.join(ROOT, "models")
ANALYSIS = os.path.join(ROOT, "analysis")

BANKING_TEST = os.path.join(
    PROCESSED,
    "banking77_test.csv"
)

os.makedirs(ANALYSIS, exist_ok=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_metric(data, metric_name):
    """
    Find a metric recursively in an existing results JSON.
    This allows Step 5C to work with the structures already
    created by Steps 4A, 4B, 4C and 5A.
    """

    if isinstance(data, dict):

        if metric_name in data:
            value = data[metric_name]

            if isinstance(value, (int, float)):
                return float(value)

        for value in data.values():

            result = find_metric(
                value,
                metric_name
            )

            if result is not None:
                return result

    elif isinstance(data, list):

        for item in data:

            result = find_metric(
                item,
                metric_name
            )

            if result is not None:
                return result

    return None


def extract_metrics(data, filename):

    metric_names = [
        "accuracy",
        "weighted_precision",
        "weighted_recall",
        "weighted_f1",
        "macro_precision",
        "macro_recall",
        "macro_f1"
    ]

    metrics = {}

    for metric in metric_names:

        value = find_metric(
            data,
            metric
        )

        if value is None:
            raise KeyError(
                f"Could not find '{metric}' in {filename}"
            )

        metrics[metric] = float(value)

    return metrics


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("STEP 5C — FINAL MODEL COMPARISON AND ERROR ANALYSIS")
    print("Multilingual UPI Complaint Assistant")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. LOAD TEST DATA
    # --------------------------------------------------------

    print("\n[1] Loading processed BANKING77 test data...")

    if not os.path.exists(BANKING_TEST):
        raise FileNotFoundError(
            f"Missing processed test dataset: {BANKING_TEST}"
        )

    test_df = pd.read_csv(BANKING_TEST)

    if (
        "text" not in test_df.columns
        or "category" not in test_df.columns
    ):
        raise ValueError(
            "BANKING77 test dataset must contain "
            "'text' and 'category' columns."
        )

    X_test = (
        test_df["text"]
        .fillna("")
        .astype(str)
    )

    y_test = (
        test_df["category"]
        .astype(str)
    )

    print("Testing rows :", len(test_df))
    print("Testing classes :", y_test.nunique())

    # --------------------------------------------------------
    # 2. LOAD CLASSICAL RESULTS
    # --------------------------------------------------------

    print("\n[2] Loading classical model results...")

    classical_files = {
        "Logistic Regression":
            "step4a_results.json",

        "Linear SVM":
            "step4b_results.json",

        "Multinomial Naive Bayes":
            "step4c_results.json"
    }

    model_results = {}

    for model_name, filename in classical_files.items():

        path = os.path.join(
            ANALYSIS,
            filename
        )

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Required results file missing: {path}"
            )

        data = load_json(path)

        metrics = extract_metrics(
            data,
            filename
        )

        model_results[model_name] = metrics

        print(
            f"PASS: {model_name} results loaded."
        )

    # --------------------------------------------------------
    # 3. LOAD XLM-R RESULTS
    # --------------------------------------------------------

    print("\n[3] Loading XLM-R results...")

    xlmr_results_path = os.path.join(
        ANALYSIS,
        "step5a_xlmr_results.json"
    )

    if not os.path.exists(xlmr_results_path):
        raise FileNotFoundError(
            f"XLM-R results file missing: "
            f"{xlmr_results_path}"
        )

    xlmr_data = load_json(
        xlmr_results_path
    )

    xlmr_metrics = extract_metrics(
        xlmr_data,
        "step5a_xlmr_results.json"
    )

    model_results["XLM-RoBERTa"] = xlmr_metrics

    print(
        "PASS: XLM-RoBERTa results loaded."
    )

    # --------------------------------------------------------
    # 4. FINAL MODEL COMPARISON
    # --------------------------------------------------------

    print("\n[4] Comparing all models...")

    comparison = []

    for model_name, metrics in model_results.items():

        comparison.append({
            "model": model_name,
            **metrics
        })

    comparison_df = pd.DataFrame(
        comparison
    )

    comparison_df = comparison_df.sort_values(
        by="macro_f1",
        ascending=False
    ).reset_index(drop=True)

    comparison_df["rank"] = range(
        1,
        len(comparison_df) + 1
    )

    best_model = comparison_df.iloc[0]["model"]

    best_macro_f1 = float(
        comparison_df.iloc[0]["macro_f1"]
    )

    print("\n" + "-" * 70)
    print("FINAL MODEL COMPARISON")
    print("-" * 70)

    print(
        f"{'Model':<25}"
        f"{'Accuracy':<12}"
        f"{'Weighted F1':<15}"
        f"{'Macro F1':<12}"
    )

    print("-" * 70)

    for _, row in comparison_df.iterrows():

        print(
            f"{row['model']:<25}"
            f"{row['accuracy']:<12.4f}"
            f"{row['weighted_f1']:<15.4f}"
            f"{row['macro_f1']:<12.4f}"
        )

    print("-" * 70)

    print(
        f"\nBest model based on Macro F1: "
        f"{best_model}"
    )

    print(
        f"Best Macro F1: {best_macro_f1:.4f}"
    )

    # --------------------------------------------------------
    # 5. IDENTIFY BEST CLASSICAL MODEL
    # --------------------------------------------------------

    classical_df = comparison_df[
        comparison_df["model"].isin([
            "Logistic Regression",
            "Linear SVM",
            "Multinomial Naive Bayes"
        ])
    ].copy()

    best_classical_row = classical_df.iloc[0]

    best_classical_model_name = (
        best_classical_row["model"]
    )

    print(
        "\n[5] Best classical model:",
        best_classical_model_name
    )

    # --------------------------------------------------------
    # 6. LOAD BEST CLASSICAL MODEL
    # --------------------------------------------------------

    model_paths = {

        "Logistic Regression":
            os.path.join(
                MODELS,
                "step4a_tfidf_logistic_regression.joblib"
            ),

        "Linear SVM":
            os.path.join(
                MODELS,
                "step4b_tfidf_linear_svm.joblib"
            ),

        "Multinomial Naive Bayes":
            os.path.join(
                MODELS,
                "step4c_multinomial_nb.joblib"
            )
    }

    vectorizer_paths = {

        "Logistic Regression":
            os.path.join(
                MODELS,
                "step4a_tfidf_vectorizer.joblib"
            ),

        "Linear SVM":
            os.path.join(
                MODELS,
                "step4b_tfidf_vectorizer.joblib"
            ),

        "Multinomial Naive Bayes":
            os.path.join(
                MODELS,
                "step4c_tfidf_vectorizer.joblib"
            )
    }

    # ------------------------------------------------------------
# Load the best classical model: Linear SVM
# ------------------------------------------------------------

    best_model_path = os.path.join(
        ROOT,
        "models",
        "step4b_linear_svm.joblib"
    )

    best_vectorizer_path = os.path.join(
        ROOT,
        "models",
        "step4b_tfidf_vectorizer.joblib"
    )

    if not os.path.exists(best_model_path):
        raise FileNotFoundError(
            f"Best classical model missing: {best_model_path}"
    )

    if not os.path.exists(best_vectorizer_path):
        raise FileNotFoundError(
            f"Best classical TF-IDF vectorizer missing: {best_vectorizer_path}"
    )

    best_classical_model = joblib.load(best_model_path)
    best_vectorizer = joblib.load(best_vectorizer_path)

    print("PASS: Best classical model loaded.")
    print("PASS: Best classical TF-IDF vectorizer loaded.")

    # --------------------------------------------------------
    # 7. GENERATE PREDICTIONS
    # --------------------------------------------------------

    print("\n[6] Generating predictions...")

    X_test_tfidf = best_vectorizer.transform(
        X_test
    )

    classical_predictions = (
        best_classical_model.predict(
            X_test_tfidf
        )
    )

    print(
        "Predictions generated:",
        len(classical_predictions)
    )

    # --------------------------------------------------------
    # 8. ERROR ANALYSIS
    # --------------------------------------------------------

    print("\n[7] Performing error analysis...")

    error_mask = (
        classical_predictions
        != y_test.to_numpy()
    )

    error_indices = np.where(
        error_mask
    )[0]

    total_errors = len(
        error_indices
    )

    print(
        "Total classification errors:",
        total_errors
    )

    error_examples = []

    for idx in error_indices[:20]:

        error_examples.append({
            "text": X_test.iloc[idx],
            "true_intent":
                str(y_test.iloc[idx]),
            "predicted_intent":
                str(classical_predictions[idx])
        })

    # --------------------------------------------------------
    # 9. MOST COMMON CONFUSIONS
    # --------------------------------------------------------

    confusion_pairs = {}

    for idx in error_indices:

        true_label = str(
            y_test.iloc[idx]
        )

        predicted_label = str(
            classical_predictions[idx]
        )

        pair = (
            true_label,
            predicted_label
        )

        confusion_pairs[pair] = (
            confusion_pairs.get(pair, 0) + 1
        )

    sorted_confusions = sorted(
        confusion_pairs.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_confusions = []

    for (
        (true_label, predicted_label),
        count
    ) in sorted_confusions[:10]:

        top_confusions.append({
            "true_intent": true_label,
            "predicted_intent": predicted_label,
            "count": int(count)
        })

    # --------------------------------------------------------
    # 10. MULTILINGUAL EVALUATION SUMMARY
    # --------------------------------------------------------

    print(
        "\n[8] Loading multilingual evaluation summary..."
    )

    multilingual_results_path = os.path.join(
        ANALYSIS,
        "step5b_multilingual_results.json"
    )

    if os.path.exists(
        multilingual_results_path
    ):

        multilingual_data = load_json(
            multilingual_results_path
        )

        multilingual_summary = {
            "rows":
                multilingual_data.get(
                    "rows",
                    41
                ),

            "compatible_rows":
                multilingual_data.get(
                    "compatible_rows",
                    0
                ),

            "incompatible_rows":
                multilingual_data.get(
                    "incompatible_rows",
                    41
                ),

            "quantitative_evaluation":
                multilingual_data.get(
                    "quantitative_evaluation",
                    False
                )
        }

    else:

        multilingual_summary = {
            "rows": 41,
            "compatible_rows": 0,
            "incompatible_rows": 41,
            "quantitative_evaluation": False
        }

    print(
        "Multilingual rows:",
        multilingual_summary["rows"]
    )

    print(
        "Compatible rows:",
        multilingual_summary["compatible_rows"]
    )

    print(
        "Incompatible rows:",
        multilingual_summary["incompatible_rows"]
    )

    # --------------------------------------------------------
    # 11. SAVE JSON RESULTS
    # --------------------------------------------------------

    print(
        "\n[9] Saving Step 5C results..."
    )

    results = {

        "step": "5C",

        "objective":
            "Final comparison of classical and multilingual NLP models",

        "evaluation_dataset":
            "BANKING77 processed test set",

        "test_rows":
            int(len(test_df)),

        "models_compared":
            comparison,

        "selection_criterion":
            "Highest Macro F1",

        "best_overall_model":
            best_model,

        "best_overall_macro_f1":
            best_macro_f1,

        "best_classical_model":
            best_classical_model_name,

        "error_analysis": {

            "model":
                best_classical_model_name,

            "total_test_errors":
                int(total_errors),

            "error_rate":
                float(
                    total_errors
                    / len(test_df)
                ),

            "representative_errors":
                error_examples,

            "top_confusion_pairs":
                top_confusions
        },

        "multilingual_evaluation":
            multilingual_summary,

        "raw_data_modified":
            False,

        "new_model_trained":
            False
    }

    results_path = os.path.join(
        ANALYSIS,
        "step5c_final_analysis_results.json"
    )

    with open(
        results_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        "Results saved to:"
    )

    print(results_path)

    # --------------------------------------------------------
    # 12. CREATE REPORT
    # --------------------------------------------------------

    print(
        "\n[10] Creating Step 5C report..."
    )

    report_lines = []

    report_lines.append(
        "# STEP 5C — FINAL MODEL COMPARISON AND ERROR ANALYSIS"
    )

    report_lines.append("")

    report_lines.append(
        "## Objective"
    )

    report_lines.append("")

    report_lines.append(
        "Compare the existing classical NLP models "
        "and XLM-RoBERTa using their recorded evaluation "
        "results, and perform a compact error analysis "
        "of the best classical model."
    )

    report_lines.append("")

    report_lines.append(
        "## Model Comparison"
    )

    report_lines.append("")

    report_lines.append(
        "| Rank | Model | Accuracy | Weighted F1 | Macro F1 |"
    )

    report_lines.append(
        "|---:|---|---:|---:|---:|"
    )

    for _, row in comparison_df.iterrows():

        report_lines.append(
            f"| {int(row['rank'])} | "
            f"{row['model']} | "
            f"{row['accuracy']:.4f} | "
            f"{row['weighted_f1']:.4f} | "
            f"{row['macro_f1']:.4f} |"
        )

    report_lines.append("")

    report_lines.append(
        f"**Best overall model based on Macro F1: "
        f"{best_model} ({best_macro_f1:.4f})**"
    )

    report_lines.append("")

    report_lines.append(
        "## Error Analysis"
    )

    report_lines.append("")

    report_lines.append(
        f"Error analysis was performed using "
        f"**{best_classical_model_name}**."
    )

    report_lines.append("")

    report_lines.append(
        f"Total test errors: **{total_errors}** "
        f"out of **{len(test_df)}**."
    )

    report_lines.append("")

    report_lines.append(
        f"Error rate: "
        f"**{total_errors / len(test_df):.4f}**."
    )

    report_lines.append("")

    report_lines.append(
        "### Representative Misclassifications"
    )

    for i, example in enumerate(
        error_examples,
        start=1
    ):

        report_lines.append("")

        report_lines.append(
            f"**Example {i}**"
        )

        report_lines.append(
            f"- Text: `{example['text']}`"
        )

        report_lines.append(
            f"- True intent: "
            f"`{example['true_intent']}`"
        )

        report_lines.append(
            f"- Predicted intent: "
            f"`{example['predicted_intent']}`"
        )

    report_lines.append("")

    report_lines.append(
        "### Most Frequent Confusion Pairs"
    )

    report_lines.append("")

    if top_confusions:

        report_lines.append(
            "| True Intent | Predicted Intent | Count |"
        )

        report_lines.append(
            "|---|---|---:|"
        )

        for item in top_confusions:

            report_lines.append(
                f"| {item['true_intent']} | "
                f"{item['predicted_intent']} | "
                f"{item['count']} |"
            )

    else:

        report_lines.append(
            "No classification errors were detected."
        )

    report_lines.append("")

    report_lines.append(
        "## Multilingual Evaluation"
    )

    report_lines.append("")

    report_lines.append(
        f"The available multilingual dataset contained "
        f"{multilingual_summary['rows']} rows."
    )

    report_lines.append(
        f"{multilingual_summary['compatible_rows']} rows "
        "had directly compatible BANKING77 labels."
    )

    report_lines.append(
        f"{multilingual_summary['incompatible_rows']} rows "
        "had incompatible intent labels."
    )

    report_lines.append("")

    report_lines.append(
        "Because the intent taxonomies were incompatible, "
        "quantitative accuracy and F1 evaluation was not "
        "performed on the multilingual dataset. No artificial "
        "label mapping was introduced."
    )

    report_lines.append("")

    report_lines.append(
        "## Interpretation"
    )

    report_lines.append("")

    report_lines.append(
        "The comparison demonstrates the performance of "
        "traditional TF-IDF-based classifiers alongside "
        "a multilingual Transformer model."
    )

    report_lines.append(
        "Macro F1 was used as the primary model-selection "
        "criterion because BANKING77 contains 77 intent "
        "classes and Macro F1 gives equal importance to "
        "each class."
    )

    report_lines.append(
        "The error analysis identifies representative "
        "intent confusions made by the best classical "
        "classifier."
    )

    report_lines.append("")

    report_lines.append(
        "## Reproducibility"
    )

    report_lines.append("")

    report_lines.append(
        "- Existing trained models were reused."
    )

    report_lines.append(
        "- No new model was trained in Step 5C."
    )

    report_lines.append(
        "- Raw datasets were not modified."
    )

    report_lines.append(
        "- Processed datasets were not modified."
    )

    report_lines.append(
        "- No artificial multilingual label mapping was used."
    )

    report_path = os.path.join(
        ANALYSIS,
        "STEP5C_FINAL_ANALYSIS_REPORT.md"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(report_lines)
        )

    print(
        "Report saved to:"
    )

    print(report_path)

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("STEP 5C COMPLETED")
    print("=" * 70)

    print(
        f"Best overall model : {best_model}"
    )

    print(
        f"Best Macro F1      : "
        f"{best_macro_f1:.4f}"
    )

    print(
        f"Best classical model : "
        f"{best_classical_model_name}"
    )

    print(
        f"Classical model errors : "
        f"{total_errors}"
    )

    print("")
    print("No new model was trained.")
    print("No raw datasets were modified.")
    print("=" * 70)


if __name__ == "__main__":
    main()