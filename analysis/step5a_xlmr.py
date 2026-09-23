import os
import json
import random
import numpy as np
import pandas as pd
import torch

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)

from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)


# ============================================================
# STEP 5A — XLM-RoBERTa MULTILINGUAL INTENT CLASSIFICATION
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

MODEL_DIR = os.path.join(
    ROOT,
    "models",
    "step5a_xlmr"
)

RESULTS_PATH = os.path.join(
    ROOT,
    "analysis",
    "step5a_xlmr_results.json"
)

REPORT_PATH = os.path.join(
    ROOT,
    "analysis",
    "STEP5A_XLMR_REPORT.md"
)

MODEL_NAME = "FacebookAI/xlm-roberta-base"

SEED = 42


# ============================================================
# REPRODUCIBILITY
# ============================================================

def set_seed(seed=42):

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ============================================================
# METRICS
# ============================================================

def compute_metrics(eval_prediction):

    predictions, labels = eval_prediction

    predictions = np.argmax(predictions, axis=1)

    accuracy = accuracy_score(
        labels,
        predictions
    )

    weighted_precision, weighted_recall, weighted_f1, _ = (
        precision_recall_fscore_support(
            labels,
            predictions,
            average="weighted",
            zero_division=0
        )
    )

    macro_precision, macro_recall, macro_f1, _ = (
        precision_recall_fscore_support(
            labels,
            predictions,
            average="macro",
            zero_division=0
        )
    )

    return {
        "accuracy": float(accuracy),
        "weighted_precision": float(weighted_precision),
        "weighted_recall": float(weighted_recall),
        "weighted_f1": float(weighted_f1),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1)
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("STEP 5A — XLM-RoBERTa MULTILINGUAL INTENT CLASSIFICATION")
    print("BANKING77")
    print("=" * 70)

    set_seed(SEED)

    # --------------------------------------------------------
    # 1. Check files
    # --------------------------------------------------------

    print("\n[1] Checking processed datasets...")

    if not os.path.exists(TRAIN_PATH):
        raise FileNotFoundError(
            f"Training file not found: {TRAIN_PATH}"
        )

    if not os.path.exists(TEST_PATH):
        raise FileNotFoundError(
            f"Testing file not found: {TEST_PATH}"
        )

    # --------------------------------------------------------
    # 2. Load data
    # --------------------------------------------------------

    print("\n[2] Loading processed datasets...")

    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    print("Training rows :", len(train_df))
    print("Testing rows  :", len(test_df))

    # --------------------------------------------------------
    # 3. Validate columns
    # --------------------------------------------------------

    required_columns = ["text", "category"]

    for column in required_columns:

        if column not in train_df.columns:
            raise ValueError(
                f"Missing training column: {column}"
            )

        if column not in test_df.columns:
            raise ValueError(
                f"Missing testing column: {column}"
            )

    # --------------------------------------------------------
    # 4. Validate 77 intents
    # --------------------------------------------------------

    train_classes = sorted(
        train_df["category"].unique()
    )

    test_classes = sorted(
        test_df["category"].unique()
    )

    combined_classes = sorted(
        set(train_classes) | set(test_classes)
    )

    print("\n[3] Checking intent classes...")

    print("Training classes :", len(train_classes))
    print("Testing classes  :", len(test_classes))
    print("Combined classes :", len(combined_classes))

    if len(combined_classes) != 77:
        raise ValueError(
            f"Expected 77 BANKING77 intents, "
            f"found {len(combined_classes)}"
        )

    # --------------------------------------------------------
    # 5. Create label mapping
    # --------------------------------------------------------

    label2id = {
        label: index
        for index, label in enumerate(combined_classes)
    }

    id2label = {
        index: label
        for label, index in label2id.items()
    }

    train_df["label"] = train_df["category"].map(
        label2id
    )

    test_df["label"] = test_df["category"].map(
        label2id
    )

    if train_df["label"].isna().any():
        raise ValueError(
            "Some training labels could not be mapped."
        )

    if test_df["label"].isna().any():
        raise ValueError(
            "Some testing labels could not be mapped."
        )

    train_df["label"] = train_df["label"].astype(int)
    test_df["label"] = test_df["label"].astype(int)

    # --------------------------------------------------------
    # 6. Convert to Hugging Face datasets
    # --------------------------------------------------------

    print("\n[4] Preparing Hugging Face datasets...")

    train_dataset = Dataset.from_pandas(
        train_df[["text", "label"]],
        preserve_index=False
    )

    test_dataset = Dataset.from_pandas(
        test_df[["text", "label"]],
        preserve_index=False
    )

    # --------------------------------------------------------
    # 7. Load XLM-R tokenizer
    # --------------------------------------------------------

    print("\n[5] Loading XLM-R tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    print("Tokenizer loaded successfully.")

    # --------------------------------------------------------
    # 8. Tokenization
    # --------------------------------------------------------

    print("\n[6] Tokenizing text...")

    def tokenize_batch(batch):

        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=128
        )

    train_dataset = train_dataset.map(
        tokenize_batch,
        batched=True
    )

    test_dataset = test_dataset.map(
        tokenize_batch,
        batched=True
    )

    print("Tokenization completed.")

    # --------------------------------------------------------
    # 9. Load XLM-R model
    # --------------------------------------------------------

    print("\n[7] Loading XLM-R sequence-classification model...")

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(combined_classes),
        id2label=id2label,
        label2id=label2id
    )

    print("Model loaded successfully.")

    # --------------------------------------------------------
    # 10. Data collator
    # --------------------------------------------------------

    data_collator = DataCollatorWithPadding(
        tokenizer=tokenizer
    )

    # --------------------------------------------------------
    # 11. Training configuration
    # --------------------------------------------------------

    print("\n[8] Preparing training configuration...")

    training_args = TrainingArguments(
        output_dir=os.path.join(
            ROOT,
            "models",
            "step5a_xlmr_training"
        ),

        eval_strategy="epoch",

        save_strategy="epoch",

        learning_rate=2e-5,

        per_device_train_batch_size=8,

        per_device_eval_batch_size=8,

        num_train_epochs=2,

        weight_decay=0.01,

        logging_steps=100,

        load_best_model_at_end=True,

        metric_for_best_model="macro_f1",

        greater_is_better=True,

        save_total_limit=1,

        report_to="none",

        seed=SEED
    )

    # --------------------------------------------------------
    # 12. Trainer
    # --------------------------------------------------------

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics
    )

    # --------------------------------------------------------
    # 13. Train
    # --------------------------------------------------------

    print("\n[9] Starting XLM-R training...")

    trainer.train()

    print("\nXLM-R training completed.")

    # --------------------------------------------------------
    # 14. Final evaluation
    # --------------------------------------------------------

    print("\n[10] Evaluating XLM-R...")

    evaluation = trainer.evaluate()

    predictions_output = trainer.predict(
        test_dataset
    )

    predictions = np.argmax(
        predictions_output.predictions,
        axis=1
    )

    true_labels = np.array(
        test_dataset["label"]
    )

    final_metrics = compute_metrics(
        (
            predictions_output.predictions,
            true_labels
        )
    )

    # --------------------------------------------------------
    # 15. Confusion matrix
    # --------------------------------------------------------

    print("\n[11] Creating confusion matrix...")

    cm = confusion_matrix(
        true_labels,
        predictions,
        labels=list(range(len(combined_classes)))
    )

    cm_path = os.path.join(
        ROOT,
        "analysis",
        "step5a_xlmr_confusion_matrix.npy"
    )

    np.save(
        cm_path,
        cm
    )

    # --------------------------------------------------------
    # 16. Save model and tokenizer
    # --------------------------------------------------------

    print("\n[12] Saving trained model...")

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    trainer.save_model(
        MODEL_DIR
    )

    tokenizer.save_pretrained(
        MODEL_DIR
    )

    # --------------------------------------------------------
    # 17. Save results
    # --------------------------------------------------------

    results = {
        "step": "5A",
        "model": "XLM-RoBERTa",
        "model_name": MODEL_NAME,
        "task": "BANKING77 intent classification",
        "num_classes": len(combined_classes),
        "training_rows": len(train_df),
        "testing_rows": len(test_df),
        "max_sequence_length": 128,
        "learning_rate": 2e-5,
        "train_batch_size": 8,
        "evaluation_batch_size": 8,
        "epochs": 2,
        "seed": SEED,
        "metrics": final_metrics,
        "evaluation_loss": float(
            evaluation.get(
                "eval_loss",
                0.0
            )
        ),
        "confusion_matrix_shape": list(
            cm.shape
        ),
        "model_path": MODEL_DIR
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as fh:

        json.dump(
            results,
            fh,
            indent=2
        )

    # --------------------------------------------------------
    # 18. Create report
    # --------------------------------------------------------

    print("\n[13] Creating Step 5A report...")

    report = f"""# STEP 5A — XLM-RoBERTa MULTILINGUAL NLP MODEL

## Objective

Step 5A introduces a multilingual Transformer model for intent
classification on the BANKING77 dataset.

The model used is XLM-RoBERTa:

`{MODEL_NAME}`

The purpose is to compare contextual multilingual Transformer
representations with the classical TF-IDF-based NLP models
implemented in Step 4.

---

## Dataset

Dataset: BANKING77

Training records: {len(train_df)}

Testing records: {len(test_df)}

Number of intent classes: {len(combined_classes)}

---

## Model

XLM-RoBERTa is a multilingual Transformer-based language model.

Unlike TF-IDF, which represents documents using independent
lexical features, XLM-R generates contextual subword
representations.

The model uses Transformer self-attention to model relationships
between tokens in context.

---

## Tokenization

XLM-R uses a SentencePiece-based subword tokenizer.

Maximum sequence length:

128 tokens

The original text is not lower-cased or translated before
tokenization.

---

## Training Configuration

- Learning rate: 2e-5
- Training batch size: 8
- Evaluation batch size: 8
- Epochs: 2
- Weight decay: 0.01
- Maximum sequence length: 128
- Random seed: {SEED}

---

## Results

| Metric | Score |
|---|---:|
| Accuracy | {final_metrics["accuracy"]:.4f} |
| Weighted Precision | {final_metrics["weighted_precision"]:.4f} |
| Weighted Recall | {final_metrics["weighted_recall"]:.4f} |
| Weighted F1 | {final_metrics["weighted_f1"]:.4f} |
| Macro Precision | {final_metrics["macro_precision"]:.4f} |
| Macro Recall | {final_metrics["macro_recall"]:.4f} |
| Macro F1 | {final_metrics["macro_f1"]:.4f} |

---

## Comparison with Classical NLP

The strongest classical model from Step 4D was:

**TF-IDF + Linear SVM**

with:

- Accuracy: 0.8926
- Macro F1: 0.8927

The XLM-R model provides a contextual multilingual representation,
whereas the classical models rely on sparse lexical TF-IDF
features.

The comparison should therefore consider not only overall
accuracy but also whether contextual multilingual representations
provide advantages for multilingual and code-mixed text.

---

## Important Scope Note

BANKING77 is primarily an English-language intent dataset.

Therefore, the Step 5A result should not be interpreted as a direct
measurement of Malayalam intent classification.

Malayalam and other multilingual/code-mixed evaluation will be
handled separately in the subsequent multilingual evaluation
stage.

No synthetic Malayalam training data is introduced in Step 5A.

---

## Reproducibility

Random seed: {SEED}

The raw datasets were not modified.

The model and tokenizer were saved separately from the raw and
processed datasets.

---

## Saved Artifacts

Model:

`models/step5a_xlmr/`

Results:

`analysis/step5a_xlmr_results.json`

Confusion matrix:

`analysis/step5a_xlmr_confusion_matrix.npy`

---

## Conclusion

Step 5A establishes the Transformer-based multilingual NLP model
for the project.

The resulting XLM-R model can be compared with the classical
TF-IDF + Linear SVM baseline before evaluating multilingual and
code-mixed behavior.
"""

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as fh:

        fh.write(report)

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("STEP 5A COMPLETED")
    print("=" * 70)

    print(
        f"\nAccuracy           : "
        f"{final_metrics['accuracy']:.4f}"
    )

    print(
        f"Weighted F1       : "
        f"{final_metrics['weighted_f1']:.4f}"
    )

    print(
        f"Macro F1          : "
        f"{final_metrics['macro_f1']:.4f}"
    )

    print("\nModel saved to:")
    print(MODEL_DIR)

    print("\nResults saved to:")
    print(RESULTS_PATH)

    print("\nReport saved to:")
    print(REPORT_PATH)

    print("\nNo raw datasets were modified.")

    print("=" * 70)


if __name__ == "__main__":
    main()