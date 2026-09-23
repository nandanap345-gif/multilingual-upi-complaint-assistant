import os
import json
import re
import numpy as np
import pandas as pd
import torch

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


# ============================================================
# PATHS
# ============================================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROCESSED = os.path.join(ROOT, "data", "processed")
MODEL_DIR = os.path.join(ROOT, "models", "step5a_xlmr")
ANALYSIS = os.path.join(ROOT, "analysis")

INPUT_FILE = os.path.join(
    PROCESSED,
    "karanverma19_multilingual_customer_support_intent_dataset.csv"
)

RESULTS_FILE = os.path.join(
    ANALYSIS,
    "step5b_multilingual_results.json"
)

REPORT_FILE = os.path.join(
    ANALYSIS,
    "STEP5B_MULTILINGUAL_EVALUATION_REPORT.md"
)

CONFUSION_FILE = os.path.join(
    ANALYSIS,
    "step5b_multilingual_confusion_matrix.npy"
)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def fail(message):
    print(f"ERROR: {message}")
    raise SystemExit(2)


def detect_script(text):
    """
    Lightweight script detection.

    Returns:
        malayalam
        latin
        mixed
        other
        empty
    """

    if not isinstance(text, str) or not text.strip():
        return "empty"

    malayalam_count = len(
        re.findall(r"[\u0D00-\u0D7F]", text)
    )

    latin_count = len(
        re.findall(r"[A-Za-z]", text)
    )

    if malayalam_count > 0 and latin_count > 0:
        return "mixed"

    if malayalam_count > 0:
        return "malayalam"

    if latin_count > 0:
        return "latin"

    return "other"


def normalize_label(label):
    """
    Conservative normalization used only for
    attempting exact label compatibility.
    """

    if pd.isna(label):
        return ""

    value = str(label).strip().lower()

    value = re.sub(r"\s+", " ", value)

    return value


def load_json(path):
    if not os.path.exists(path):
        fail(f"Missing file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("STEP 5B — MULTILINGUAL EVALUATION")
    print("Existing XLM-R + karanverma19 multilingual dataset")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Check files
    # --------------------------------------------------------

    print("\n[1] Checking required files...")

    if not os.path.exists(INPUT_FILE):
        fail(f"Missing processed multilingual dataset: {INPUT_FILE}")

    if not os.path.exists(MODEL_DIR):
        fail(f"Missing trained XLM-R model: {MODEL_DIR}")

    print("PASS: Multilingual dataset exists.")
    print("PASS: XLM-R model exists.")

    # --------------------------------------------------------
    # 2. Load multilingual dataset
    # --------------------------------------------------------

    print("\n[2] Loading multilingual dataset...")

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "query",
        "intent",
        "language",
        "category"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        fail(f"Missing required columns: {missing}")

    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # --------------------------------------------------------
    # 3. Dataset language/script analysis
    # --------------------------------------------------------

    print("\n[3] Analyzing language and script characteristics...")

    df["script_type"] = df["query"].apply(detect_script)

    script_counts = (
        df["script_type"]
        .value_counts()
        .to_dict()
    )

    language_counts = (
        df["language"]
        .fillna("unknown")
        .astype(str)
        .value_counts()
        .to_dict()
    )

    print("Script distribution:")

    for key, value in script_counts.items():
        print(f"  {key}: {value}")

    print("\nLanguage distribution:")

    for key, value in language_counts.items():
        print(f"  {key}: {value}")

    # --------------------------------------------------------
    # 4. Load BANKING77 label mapping from trained XLM-R
    # --------------------------------------------------------

    print("\n[4] Loading XLM-R label mapping...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_DIR
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_DIR
    )

    model.eval()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    model.to(device)

    id2label = model.config.id2label

    if not id2label:
        fail("XLM-R model does not contain id2label mapping.")

    banking_labels = {
        normalize_label(label): int(idx)
        for idx, label in id2label.items()
    }

    print(
        f"PASS: Loaded {len(banking_labels)} XLM-R labels."
    )

    # --------------------------------------------------------
    # 5. Determine compatible multilingual labels
    # --------------------------------------------------------

    print("\n[5] Checking label compatibility...")

    df["_normalized_intent"] = (
        df["intent"]
        .apply(normalize_label)
    )

    df["_normalized_category"] = (
        df["category"]
        .apply(normalize_label)
    )

    compatible_using_intent = (
        df["_normalized_intent"]
        .isin(banking_labels.keys())
    )

    compatible_using_category = (
        df["_normalized_category"]
        .isin(banking_labels.keys())
    )

    # Prefer exact intent match.
    df["_compatible"] = compatible_using_intent

    # If intent is unavailable, allow exact category match.
    df.loc[
        ~df["_compatible"],
        "_compatible"
    ] = compatible_using_category[
        ~df["_compatible"]
    ]

    compatible_df = df[df["_compatible"]].copy()

    incompatible_df = df[~df["_compatible"]].copy()

    print(
        f"Compatible rows: {len(compatible_df)}"
    )

    print(
        f"Incompatible rows: {len(incompatible_df)}"
    )

    # --------------------------------------------------------
    # 6. Do not fabricate mappings
    # --------------------------------------------------------

    if len(compatible_df) == 0:

        print(
            "\nNo exact BANKING77-compatible labels were found."
        )

        evaluation_status = (
            "not_evaluable_due_to_label_incompatibility"
        )

        metrics = {
            "accuracy": None,
            "weighted_precision": None,
            "weighted_recall": None,
            "weighted_f1": None,
            "macro_precision": None,
            "macro_recall": None,
            "macro_f1": None,
        }

        confusion_shape = None

    else:

        print(
            "\nExact compatible labels found."
        )

        # ----------------------------------------------------
        # 7. Prepare labels
        # ----------------------------------------------------

        y_true = []

        for _, row in compatible_df.iterrows():

            intent = normalize_label(
                row["intent"]
            )

            category = normalize_label(
                row["category"]
            )

            if intent in banking_labels:
                label_id = banking_labels[intent]

            elif category in banking_labels:
                label_id = banking_labels[category]

            else:
                continue

            y_true.append(label_id)

        compatible_df = compatible_df.iloc[
            :len(y_true)
        ].copy()

        texts = (
            compatible_df["query"]
            .fillna("")
            .astype(str)
            .tolist()
        )

        y_true = np.array(
            y_true,
            dtype=int
        )

        # ----------------------------------------------------
        # 8. XLM-R prediction
        # ----------------------------------------------------

        print("\n[6] Generating XLM-R predictions...")

        predictions = []

        batch_size = 8

        for start in range(
            0,
            len(texts),
            batch_size
        ):

            batch_texts = texts[
                start:start + batch_size
            ]

            encoded = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="pt"
            )

            encoded = {
                key: value.to(device)
                for key, value in encoded.items()
            }

            with torch.no_grad():

                outputs = model(
                    **encoded
                )

                batch_predictions = (
                    torch.argmax(
                        outputs.logits,
                        dim=1
                    )
                    .cpu()
                    .numpy()
                    .tolist()
                )

            predictions.extend(
                batch_predictions
            )

        y_pred = np.array(
            predictions,
            dtype=int
        )

        print(
            f"Predictions generated: {len(y_pred)}"
        )

        # ----------------------------------------------------
        # 9. Evaluation
        # ----------------------------------------------------

        print("\n[7] Evaluating multilingual subset...")

        accuracy = accuracy_score(
            y_true,
            y_pred
        )

        weighted_precision, weighted_recall, weighted_f1, _ = (
            precision_recall_fscore_support(
                y_true,
                y_pred,
                average="weighted",
                zero_division=0
            )
        )

        macro_precision, macro_recall, macro_f1, _ = (
            precision_recall_fscore_support(
                y_true,
                y_pred,
                average="macro",
                zero_division=0
            )
        )

        metrics = {
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
            ),
        }

        labels_present = sorted(
            set(y_true.tolist()) |
            set(y_pred.tolist())
        )

        cm = confusion_matrix(
            y_true,
            y_pred,
            labels=labels_present
        )

        np.save(
            CONFUSION_FILE,
            cm
        )

        confusion_shape = list(
            cm.shape
        )

        evaluation_status = "evaluated"

        print("\n--------------------------------------------------")
        print("MULTILINGUAL EVALUATION RESULTS")
        print("--------------------------------------------------")
        print(
            f"Accuracy           : {accuracy:.4f}"
        )
        print(
            f"Weighted Precision : {weighted_precision:.4f}"
        )
        print(
            f"Weighted Recall    : {weighted_recall:.4f}"
        )
        print(
            f"Weighted F1        : {weighted_f1:.4f}"
        )
        print(
            f"Macro Precision    : {macro_precision:.4f}"
        )
        print(
            f"Macro Recall       : {macro_recall:.4f}"
        )
        print(
            f"Macro F1           : {macro_f1:.4f}"
        )

    # --------------------------------------------------------
    # 10. Save results
    # --------------------------------------------------------

    print("\n[8] Saving results...")

    results = {

        "step": "5B",

        "title": (
            "Multilingual evaluation using "
            "existing XLM-R model"
        ),

        "dataset": (
            "karanverma19_multilingual_customer_support"
        ),

        "total_rows": int(len(df)),

        "compatible_rows": int(
            len(compatible_df)
        ),

        "incompatible_rows": int(
            len(incompatible_df)
        ),

        "evaluation_status": evaluation_status,

        "script_distribution": {
            str(k): int(v)
            for k, v in script_counts.items()
        },

        "language_distribution": {
            str(k): int(v)
            for k, v in language_counts.items()
        },

        "metrics": metrics,

        "confusion_matrix_shape": confusion_shape,

        "model": "XLM-RoBERTa",

        "model_source": (
            "existing Step 5A trained model"
        ),

        "training_performed_in_step5b": False,

        "raw_data_modified": False,

        "label_mapping_policy": (
            "Only exact BANKING77-compatible "
            "intent/category labels were evaluated. "
            "No synthetic or manually fabricated "
            "label mappings were introduced."
        ),

        "malayalam_policy": (
            "Malayalam data was not fabricated, "
            "translated, or transliterated."
        )
    }

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Results saved to:\n{RESULTS_FILE}"
    )

    # --------------------------------------------------------
    # 11. Create concise report
    # --------------------------------------------------------

    print("\n[9] Creating Step 5B report...")

    report = f"""# STEP 5B — MULTILINGUAL EVALUATION

## Objective

Evaluate the already-trained XLM-RoBERTa model from Step 5A
on the available multilingual customer-support dataset without
retraining the model.

## Dataset

- Dataset: karanverma19 multilingual customer support dataset
- Total rows: {len(df)}
- Compatible rows evaluated: {len(compatible_df)}
- Incompatible rows: {len(incompatible_df)}

## Language Distribution

{json.dumps(language_counts, indent=2, ensure_ascii=False)}

## Script Distribution

{json.dumps(script_counts, indent=2, ensure_ascii=False)}

## Label Compatibility

Only exact BANKING77-compatible intent/category labels were
accepted for quantitative evaluation.

No manual, synthetic, guessed, translated, or fabricated
label mappings were introduced.

This prevents an invalid comparison between unrelated intent
taxonomies.

## Evaluation Status

**{evaluation_status}**

## Metrics

{json.dumps(metrics, indent=2)}

## Model

- XLM-RoBERTa
- Existing trained model from Step 5A
- No additional training performed in Step 5B

## Malayalam Policy

Malayalam data is not fabricated, translated, or transliterated.
Native-script and Romanized text are preserved as provided.

## Data Integrity

- Raw datasets were not modified.
- No preprocessing was fitted on the evaluation dataset.
- No additional model training was performed.
- Only the existing Step 5A XLM-R model was used.

## Reproducibility

Results are stored in:

`analysis/step5b_multilingual_results.json`

"""

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    print(
        f"Report saved to:\n{REPORT_FILE}"
    )

    print("\n" + "=" * 70)
    print("STEP 5B COMPLETED")
    print("=" * 70)

    if evaluation_status == "evaluated":

        print(
            f"Accuracy   : "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"Weighted F1: "
            f"{metrics['weighted_f1']:.4f}"
        )

        print(
            f"Macro F1   : "
            f"{metrics['macro_f1']:.4f}"
        )

    else:

        print(
            "Quantitative evaluation was not performed "
            "because the dataset labels were not directly "
            "compatible with BANKING77."
        )

    print("\nNo XLM-R retraining performed.")
    print("No raw datasets modified.")
    print("=" * 70)


if __name__ == "__main__":
    main()