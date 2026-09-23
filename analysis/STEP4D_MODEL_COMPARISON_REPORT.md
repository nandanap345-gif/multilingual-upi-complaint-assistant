# STEP 4D — CLASSICAL NLP MODEL COMPARISON

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
| TF-IDF + Logistic Regression | 0.8425 | 0.8563 | 0.8425 | 0.8404 | 0.8563 | 0.8423 | 0.8403 |
| TF-IDF + Linear SVM | 0.8926 | 0.8966 | 0.8926 | 0.8927 | 0.8966 | 0.8926 | 0.8927 |
| TF-IDF + Multinomial Naive Bayes | 0.8366 | 0.8521 | 0.8366 | 0.8326 | 0.8523 | 0.8363 | 0.8325 |

---

## Best Classical NLP Model

**Linear SVM** is selected as the strongest classical NLP
baseline because it achieved the highest Macro F1 score.

Its Macro F1 score is:

**0.8927**

Its accuracy is:

**0.8926**

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
