# STEP 5B — MULTILINGUAL EVALUATION

## Objective

Evaluate the already-trained XLM-RoBERTa model from Step 5A
on the available multilingual customer-support dataset without
retraining the model.

## Dataset

- Dataset: karanverma19 multilingual customer support dataset
- Total rows: 41
- Compatible rows evaluated: 0
- Incompatible rows: 41

## Language Distribution

{
  "Hindi": 15,
  "Hinglish": 12,
  "English": 7,
  "Punjabi": 7
}

## Script Distribution

{
  "latin": 41
}

## Label Compatibility

Only exact BANKING77-compatible intent/category labels were
accepted for quantitative evaluation.

No manual, synthetic, guessed, translated, or fabricated
label mappings were introduced.

This prevents an invalid comparison between unrelated intent
taxonomies.

## Evaluation Status

**not_evaluable_due_to_label_incompatibility**

## Metrics

{
  "accuracy": null,
  "weighted_precision": null,
  "weighted_recall": null,
  "weighted_f1": null,
  "macro_precision": null,
  "macro_recall": null,
  "macro_f1": null
}

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

