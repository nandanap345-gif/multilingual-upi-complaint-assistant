# STEP 4C — MULTINOMIAL NAIVE BAYES

## Objective

Train and evaluate a Multinomial Naive Bayes classifier for BANKING77 intent classification using TF-IDF text representations.

## Dataset

- Dataset: BANKING77
- Training rows: 10003
- Testing rows: 3073
- Number of intents: 77

## Text Representation

TF-IDF was used to convert customer-support text into numerical feature vectors.

Configuration:

- n-gram range: (1, 2)
- lowercase: False
- sublinear TF: True
- Vocabulary size: 25523

## Model

Multinomial Naive Bayes was used as a lightweight probabilistic text-classification model.

Hyperparameter:

- alpha: 0.1

## Evaluation Metrics

| Metric | Score |
|---|---:|
| Accuracy | 0.836642 |
| Weighted Precision | 0.852087 |
| Weighted Recall | 0.836642 |
| Weighted F1 | 0.832584 |
| Macro Precision | 0.852277 |
| Macro Recall | 0.836346 |
| Macro F1 | 0.832479 |

## Interpretation

The Multinomial Naive Bayes model provides a lightweight probabilistic baseline for comparison with the Logistic Regression and Linear SVM models developed in Steps 4A and 4B.

The model is evaluated on the same processed BANKING77 test set used by the other baseline models.

## Reproducibility

The trained model and TF-IDF vectorizer were saved as separate artifacts.

Model:
`C:\Users\nanda\Downloads\Multilingual_UPI_Complaint_Assistant\models\step4c_multinomial_nb.joblib`

Vectorizer:
`C:\Users\nanda\Downloads\Multilingual_UPI_Complaint_Assistant\models\step4c_tfidf_vectorizer.joblib`

## Modeling Scope

Only the processed BANKING77 dataset was used for this baseline model.

No raw dataset was modified.

Generated on:
`2026-08-16T11:52:23.995861+00:00`
