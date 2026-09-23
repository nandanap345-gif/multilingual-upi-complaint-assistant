# Annotation Guidelines

This document defines annotation rules for UPI complaint records.

Annotators must assign the following fields for each record:

A. Intent
B. Language
C. Script
D. Writing style

General rules

- Preserve the original `complaint_text` exactly; do not modify it in the raw data file.
- When assigning intent, choose the most specific label applicable from the taxonomy.
- If the complaint explicitly states that money was deducted despite failure, prefer `MONEY_DEDUCTED_PAYMENT_FAILED` over `PAYMENT_FAILED`.
- If the annotator cannot confidently determine an intent, mark `intent` as `OTHER_UPI_COMPLAINT` and set `validation_status` accordingly.
- All researcher-created examples must be labelled with `source_type` = `RESEARCHER_CREATED` (or `SYNTHETIC`/`AUGMENTED` where appropriate).
- Annotators must never record or transcribe sensitive financial information such as transaction numbers, account numbers, UPI IDs, phone numbers, OTPs, PINs, card numbers, or addresses. If such information appears, remove or redact it and record a note in the annotation platform (do not store sensitive data in the CSV or repo).

Intent annotation rules

- Choose the most specific applicable intent label from the taxonomy.
- Do not invent new intent categories. If an example does not fit, use `OTHER_UPI_COMPLAINT` and record a short note for later taxonomy review.

Language annotation rules

- Identify the dominant language of the complaint and record it in `language`.
- If multiple languages are present and no single dominant language exists, choose the language of primary semantic content.
- If the text contains multiple languages but one is dominant, label `writing_style` = `CODE_MIXED`.

Script annotation rules

- Record the script used for the text in `script` (e.g., Latin, Devanagari, Malayalam, Tamil, Telugu, Kannada).
- For mixed scripts, record `script` = `mixed` and set `writing_style` appropriately.

Writing-style annotation rules

- `ENGLISH`: Text in English using Latin script.
- `NATIVE_SCRIPT`: Text written using a regional script (Devanagari, Malayalam, Tamil, Telugu, Kannada, etc.).
- `ROMANIZED`: Regional language content written with Latin characters.
- `CODE_MIXED`: A mix of English and a regional language in the same complaint.
- `INFORMAL`: Heavy non-standard spelling, abbreviations, or colloquial forms; dialectal variants.

Validation and quality control

- Each researcher-created base complaint and its linguistic variants must be validated by a human annotator familiar with the relevant language.
- Validation should confirm that intent and language labels are preserved and that the text reads naturally for native speakers.
- Record `annotator_id` for each annotator (use anonymized IDs, not real names).
- Record `validation_status` as one of: `PENDING`, `VALIDATED`, `REJECTED`.
- If `REJECTED`, include a short reason in the annotation platform.

Annotator conduct and privacy

- Do not transcribe or store any sensitive financial data.
- Do not attempt to de-anonymize or contact users whose example text might be discovered.
- Follow institutional review and privacy guidelines when working with any publicly available data.

Notes

- These guidelines are for Phase 2 planning only and do not involve dataset creation at this stage.
