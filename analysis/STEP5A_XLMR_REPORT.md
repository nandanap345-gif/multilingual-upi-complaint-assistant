# STEP 5A — XLM-RoBERTa MULTILINGUAL NLP MODEL

## Objective

Step 5A introduces a multilingual Transformer model for intent
classification on the BANKING77 dataset.

The model used is XLM-RoBERTa:

`FacebookAI/xlm-roberta-base`

The purpose is to compare contextual multilingual Transformer
representations with the classical TF-IDF-based NLP models
implemented in Step 4.

---

## Dataset

Dataset: BANKING77

Training records: 10003

Testing records: 3073

Number of intent classes: 77

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
- Random seed: 42

---

## Results

| Metric | Score |
|---|---:|
| Accuracy | 0.8292 |
| Weighted Precision | 0.8471 |
| Weighted Recall | 0.8292 |
| Weighted F1 | 0.8050 |
| Macro Precision | 0.8472 |
| Macro Recall | 0.8288 |
| Macro F1 | 0.8048 |

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

Random seed: 42

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
