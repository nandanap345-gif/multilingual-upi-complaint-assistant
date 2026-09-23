# Step 3G Preprocessing Report

## Objective

Create reproducible processed copies of the selected datasets for later modeling using conservative, deterministic text normalization only.

Raw datasets in `data/raw_data/` were not modified.

---

## Datasets Processed

### BANKING77

- Raw training file: `data/raw_data/banking77_train.csv`
- Raw test file: `data/raw_data/banking77_test.csv`
- Processed training file: `data/processed/banking77_train.csv`
- Processed test file: `data/processed/banking77_test.csv`

### karanverma19

- Raw file: `data/raw_data/karanverma19_multilingual_customer_support_intent_dataset.csv`
- Processed file: `data/processed/karanverma19_multilingual_customer_support_intent_dataset.csv`

---

## Banking77

- train input rows: 10003
- test input rows: 3080
- train output rows: 10003
- test output rows: 3073
- unique intents (combined): 77
- train duplicates: 4
- test duplicates: 1
- cross-split duplicates removed from processed test: 7
- cross-split duplicates (original in raw): 7
- cross-split duplicates after preprocessing: 0

The seven cross-split duplicate texts identified in the raw BANKING77 train/test data were removed from the processed test set to prevent train/test leakage. The processed training set was not modified for this reason.

The original raw train/test split was otherwise preserved. No merging, shuffling, or re-splitting was performed.

---

## karanverma19

- input rows: 41
- output rows: 41
- duplicates: 0

All original records were retained.

---

## Missing Text Counts

- banking_train missing text: 0
- banking_test missing text: 0
- karan missing text: 0

No records were dropped because of missing text.

---

## Text Normalization Policy

The preprocessing applies conservative normalization only:

- Unicode normalization using NFKC.
- Multiple whitespace characters are collapsed into a single ASCII space.
- Leading and trailing whitespace is removed.
- Punctuation is preserved.
- Original casing is preserved.
- Original language/script is preserved.
- Romanized text is not transliterated.
- Code-mixed text is not translated or converted.
- No synthetic text is generated.
- No data augmentation is performed.

---

## Language and Script Preservation

The preprocessing does not translate, transliterate, or otherwise convert the language or script of the source text.

Romanized text remains Romanized.

Code-mixed text remains code-mixed.

Native-script text remains in its original script.

---

## Malayalam Policy

Malayalam is retained as a documented language/resource scope and limitation, but no synthetic or translated Malayalam training data is introduced in Step 3G.

No Malayalam rows were fabricated, translated, transliterated, or added during preprocessing.

The absence of Malayalam records in the selected raw datasets is therefore preserved in the processed datasets.

---

## Leakage Prevention

Train/test leakage was explicitly checked during Step 3G.

The raw BANKING77 datasets contained:

- 7 duplicate text records occurring across the original train and test splits.

These were removed from the processed test set.

After preprocessing:

- Processed train/test overlapping texts: 0
- Processed train/test text leakage detected: No

No vocabulary, tokenizer, statistical transformation, or model was fitted during Step 3G.

Any transformations that require fitting on data will be performed only using the training data in the appropriate later modeling stage.

---

## Train/Test Separation

The original BANKING77 train/test separation was preserved.

- Training data were processed only from the raw training file.
- Test data were processed only from the raw test file.
- No train/test merging was performed.
- No random re-splitting was performed.
- No shuffling-based reallocation between train and test was performed.
- The seven identified cross-split duplicate records were removed from the processed test set solely to prevent leakage.

---

## Duplicate Handling

Duplicates were audited before and after preprocessing.

### BANKING77

- Training duplicates: 4
- Test duplicates: 1
- Raw cross-split duplicates: 7
- Cross-split duplicates removed from processed test: 7
- Processed cross-split duplicates: 0

Duplicates within an individual split were not automatically removed unless they were identified as cross-split duplicates that could cause train/test leakage.

### karanverma19

- Duplicate records: 0

---

## Examples of Normalization

The following examples illustrate representative processed text:

- `I am still waiting on my card?`
- `What can I do if my card still hasn't arrived after 2 weeks?`
- `I have been waiting over a week. Is the card still coming?`

Normalization is intentionally conservative so that punctuation, casing, linguistic patterns, and code-mixed or Romanized signals are not unnecessarily destroyed.

---

## Raw Data Integrity

The raw datasets under `data/raw_data/` were not modified.

Verified raw row counts:

- BANKING77 train: 10003
- BANKING77 test: 3080
- BANKING77 combined: 13083
- karanverma19: 41

Processed row counts:

- BANKING77 train: 10003
- BANKING77 test: 3073
- BANKING77 combined processed: 13076
- karanverma19: 41

The difference between the raw and processed BANKING77 test count is explained by the seven cross-split duplicate records removed to prevent train/test leakage.

---

## Modeling Status

Step 3G is a preprocessing and data-integrity stage only.

- Modeling started: No
- Model training performed: No
- Model artifacts created: No
- Translation performed: No
- Transliteration performed: No
- Data augmentation performed: No
- Synthetic Malayalam data generated: No

---

## Reproducibility

The preprocessing is implemented through:

`analysis/step3g_preprocess.py`

The preprocessing configuration is recorded in:

`analysis/step3g_preprocessing_config.json`

The validation procedure is implemented through:

`analysis/validate_step3g.py`

The duplicate audit is recorded in:

`analysis/step3g_duplicate_audit.json`

and:

`analysis/STEP3G_DUPLICATE_AUDIT.md`

The processed datasets are stored separately from the raw datasets under:

`data/processed/`

---

## Step 3G Conclusion

Step 3G preprocessing was completed using conservative normalization and explicit leakage prevention.

The raw datasets remain unchanged. The processed datasets preserve the original fields, labels, language/script characteristics, and train/test separation, except for the seven cross-split duplicate texts removed from the processed BANKING77 test set to eliminate train/test leakage.

No modeling or training was performed during this step.

Step 3G preprocessing and validation are complete.