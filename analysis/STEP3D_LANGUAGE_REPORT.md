# Step 3D: Language Identification — Report

Purpose: establish observed language composition of available datasets (read-only).

## Dataset language metadata
- karanverma19: language labels supplied by dataset in `language` column.
- BANKING77: documented as English (dataset metadata).

## karanverma19 language distribution
- total records: 41
- unique language labels: English, Hindi, Hinglish, Punjabi

Language counts:
- Hindi: 15 (36.59%)
- English: 7 (17.07%)
- Hinglish: 12 (29.27%)
- Punjabi: 7 (17.07%)

Language × intent distribution: (see JSON `language_intent_distribution`)

Representative examples (exact text from dataset):
- Hindi:
  - Refund kab milega?
  - Mera account block ho gaya hai
  - Paise kat gaye par recharge nahi hua
- English:
  - My payment failed but money deducted
  - How do I reset my account password?
  - Why was my payment declined?
- Hinglish:
  - Order abhi tak deliver nahi hua
  - Delivery late kyun hai?
  - Recharge successful dikh raha hai but service chalu nahi hui
- Punjabi:
  - Mera refund kado milega?
  - Parcel ajj tak nahi aaya
  - Refund process kiven hovega?

## BANKING77 observational language check
- total records (train+test): 13083
- ASCII-only texts: 13022 (99.53%)
- non-ASCII texts: 61
- texts containing Indic-script characters: 0

Representative BANKING77 examples containing Indic-script characters (if any):

## Romanized / transliterated text
- karanverma19: language metadata may indicate romanized labels if present; analysis lists labels as-is.
- BANKING77: predominantly ASCII/Latin script; romanized Indian-language identification cannot be reliably inferred from ASCII-only text.

## Code-mixing (observational)
- Script-based inspection alone cannot reliably identify code-mixing. Code-mixed text may involve different languages written in the same Latin/Roman script, such as English mixed with Romanized Indian-language text. Therefore, the detailed identification of code-mixed and Romanized text is deferred to the subsequent analysis step. See JSON for flagged examples.

## Limitations
- karanverma19 contains only 41 records; conclusions exploratory.
- `language` column is dataset-supplied metadata and may not be ground truth.
- BANKING77 is an English dataset and provides limited multilingual signal.
- Romanized Indian-language detection is non-trivial for ASCII text; further methods required.
 - Malayalam is currently absent from the acquired datasets (BANKING77 and karanverma19). Therefore, no conclusions about Malayalam NLP performance or presence should be drawn from these datasets.

## Key conclusions
- karanverma19 provides explicit language metadata; see JSON counts and figures.
- BANKING77 is predominantly ASCII/Latin script and aligns with dataset documentation stating English.
