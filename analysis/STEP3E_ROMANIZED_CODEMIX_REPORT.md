# Step 3E: Romanized and Code-Mixed Text — Exploratory Report

Purpose: exploratory identification of Romanized and code-mixed examples in karanverma19 (read-only).

## A. karanverma19 per-language breakdown (labels from dataset)
- total records: 41

### Hinglish
- count: 12
- percent: 29.27%
- representative examples:
  - Order abhi tak deliver nahi hua
  - Delivery late kyun hai?
  - Recharge successful dikh raha hai but service chalu nahi hui
- observed linguistic characteristics:
  - informal spellings, phonetic renderings, mixed English tokens (see examples)

### Hindi
- count: 15
- percent: 36.59%
- representative examples:
  - Refund kab milega?
  - Mera account block ho gaya hai
  - Paise kat gaye par recharge nahi hua
- observed linguistic characteristics:
  - informal spellings, phonetic renderings, mixed English tokens (see examples)

### Punjabi
- count: 7
- percent: 17.07%
- representative examples:
  - Mera refund kado milega?
  - Parcel ajj tak nahi aaya
  - Refund process kiven hovega?
- observed linguistic characteristics:
  - informal spellings, phonetic renderings, mixed English tokens (see examples)

### English
- count: 7
- percent: 17.07%
- representative examples:
  - My payment failed but money deducted
  - How do I reset my account password?
  - Why was my payment declined?
- observed linguistic characteristics:
  - informal spellings, phonetic renderings, mixed English tokens (see examples)

## B. Romanized text observations
- Heuristics used (conservative): presence of high-precision romanized markers (e.g., "hai", "nahi", "kab", "kyun", "paise"). Phonetic-ending rules were intentionally removed to avoid over-classification.
- Representative likely-romanized examples are listed below and in the JSON output.

## C. Code-mixing (exploratory candidates)
- Conservative approach: require stronger evidence of two language components (e.g., multiple English tokens together with explicit romanized markers) before flagging as possible code-mixed. Single English loanwords (refund, order, payment, delivery, recharge, etc.) inside romanized text are treated as loanword usages and are insufficient on their own to establish code-mixing.
- See JSON for per-example heuristics and the script's conservative manual-review decisions.

## G. Manual per-record reviews (exploratory)

These are exploratory manually reviewed observations, not gold-standard linguistic annotations.

Per-language flagged records (original text, dataset label, heuristic reason, final exploratory assessment):

### Hinglish
- "Order abhi tak deliver nahi hua" — label: Hinglish — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Delivery late kyun hai?" — label: Hinglish — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Recharge successful dikh raha hai but service chalu nahi hui" — label: Hinglish — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Payment ho gaya par ticket book nahi hui" — label: Hinglish — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Order return request ka status kya hai?" — label: Hinglish — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Delivery address galat update ho gaya" — label: Hinglish — heuristic: no clear romanized markers or mixed evidence — assessment: uncertain
-- "Recharge fail ho gaya but amount deducted" — label: Hinglish — heuristic: no clear romanized markers or mixed evidence — assessment: uncertain

### Hindi
- "Refund kab milega?" — label: Hindi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Mera account block ho gaya hai" — label: Hindi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Paise kat gaye par recharge nahi hua" — label: Hindi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Mera order cancel ho gaya without reason" — label: Hindi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Mera bank account access nahi ho raha" — label: Hindi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Payment do baar deduct ho gaya" — label: Hindi — heuristic: no clear romanized markers or mixed evidence — assessment: uncertain

### Punjabi
- "Mera refund kado milega?" — label: Punjabi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Parcel ajj tak nahi aaya" — label: Punjabi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Late delivery de karke complaint karni hai" — label: Punjabi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Mera package wrong address te chala gaya" — label: Punjabi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
- "Order delay de bare complaint karni hai" — label: Punjabi — heuristic: romanized markers (possibly with English loanword) — assessment: likely Romanized
  - "Refund amount mere account vich nahi aaya" — label: Punjabi — heuristic: romanized markers + 2 English tokens — assessment: uncertain
- "Refund process kiven hovega?" — label: Punjabi — heuristic: no clear romanized markers or mixed evidence — assessment: uncertain

### English
- All 7 English-labelled records were marked uncertain by the conservative heuristics; examples include:
  - "My payment failed but money deducted" — heuristic: no clear romanized markers or mixed evidence — assessment: uncertain
  - "How do I reset my account password?" — heuristic: no clear romanized markers or mixed evidence — assessment: uncertain


## D. BANKING77 brief comparison
- total records: 13083; predominantly English per dataset documentation.
- Sample informal examples (small sample) provided in JSON.

## E. Limitations
- karanverma19 has only 41 records; findings exploratory.
- `language` column is dataset-provided metadata and may not be ground truth.
- Romanized detection heuristics are not exhaustive; manual annotation required for gold labels.
- Code-mixing can occur within the same script; script-based checks are insufficient.
 - Malayalam is currently absent from the acquired datasets (BANKING77 and karanverma19). Therefore, no conclusions about Malayalam NLP performance or presence should be drawn from these datasets.

## F. Summary table (exploratory)
- See JSON `karan_summary_table` for an explicit table of counts per label and exploratory flags.