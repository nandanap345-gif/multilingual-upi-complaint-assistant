# Step 3G Preprocessing Plan

Objective
---------
Create reproducible processed copies of the selected datasets for later modeling, using conservative normalization only. Do not modify raw data in `data/raw_data/`.

Datasets selected for preprocessing
- `data/raw_data/banking77_train.csv` (BANKING77 train)
- `data/raw_data/banking77_test.csv` (BANKING77 test)
- `data/raw_data/karanverma19_multilingual_customer_support_intent_dataset.csv` (karanverma19)

Fields used
- BANKING77: `text`, `category` (use both)
- karanverma19: `query`, `intent`, `language`, `category` (preserve all)

Fields excluded and why
- None excluded; preserve existing fields to keep provenance and labels.

Missing-value handling
- If a text field is missing or empty after stripping, set it to an empty string and record as a missing-text case in the preprocessing report; do not drop rows.

Duplicate handling
- Do not drop duplicates automatically. Record duplicate counts pre/post.
- Ensure no duplicate record crosses train/test boundaries; if found, record in report and preserve original split.

Text normalization policy
- Unicode normalization: apply `NFKC` normalization to text fields.
- Whitespace normalization: collapse multiple whitespace to a single space; trim surrounding whitespace.
- Punctuation: preserve punctuation (no removal), except normalize common non-breaking spaces.
- Casing: preserve original casing to maintain linguistic signals.

Whitespace normalization
- Replace any sequence of whitespace characters (\s+) with a single ASCII space; strip leading/trailing spaces.

Unicode handling
- Use `unicodedata.normalize('NFKC', text)` for conservative normalization.

Casing policy
- Preserve original casing (do not lower-case) to retain named entities and code-mixed cues.

Language/script preservation policy
- Preserve original script and encoding; do not transliterate, translate, or convert Romanized text to native script.

Treatment of Romanized text
- Leave Romanized strings unchanged except for normalization and whitespace cleanup.

Treatment of code-mixed text
- Preserve code-mixed text as-is, only apply normalization and whitespace policies.

Malayalam handling
- Explicitly retain Malayalam in its original form (native Malayalam script or romanized). Do NOT fabricate, translate, or transliterate Malayalam data.
- Statement to include in report: "Malayalam is retained as a documented language/resource scope and limitation, but no synthetic or translated Malayalam training data is introduced in Step 3G."

Leakage-prevention rules
- Fit any vocabulary or statistical transformations only on training data (future steps). For Step 3G no such fitting occurs.
- Ensure processed training files are created from raw training files only; processed test files are created from raw test files only.

Train/test separation rules
- Preserve original train/test splits strictly; do not merge, shuffle, or re-split.

Output locations
- `data/processed/banking77_train.csv`
- `data/processed/banking77_test.csv`
- `data/processed/karanverma19_multilingual_customer_support_intent_dataset.csv`

Audit and reproducibility
- The preprocessing script will be deterministic and include logging of operations, row counts, duplicate counts, and examples of normalization.
