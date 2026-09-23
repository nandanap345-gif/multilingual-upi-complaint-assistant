# STEP 4A — BASELINE MODELING REPORT

## Objective

Establish a reproducible classical NLP baseline for BANKING77
intent classification before evaluating stronger machine-learning
and multilingual transformer approaches.

## Dataset

- Dataset: BANKING77
- Training rows: 10003
- Testing rows: 3073
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

- 25523

Training matrix:

- (10003, 25523)

Testing matrix:

- (3073, 25523)

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
| Accuracy | 0.8425 |
| Weighted Precision | 0.8563 |
| Weighted Recall | 0.8425 |
| Weighted F1 | 0.8404 |
| Macro Precision | 0.8563 |
| Macro Recall | 0.8423 |
| Macro F1 | 0.8403 |

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
