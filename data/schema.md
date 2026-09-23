# Data Schema

This document defines the dataset schema for UPI complaint records used in the project.

Fields

- `complaint_id`: Unique identifier for the record (string).
- `complaint_text`: Original complaint text (string). Preserve exactly as received.
- `intent`: One of the defined complaint taxonomy labels (see below).
- `language`: Primary language associated with the complaint (see language list).
- `script`: Writing script or orthography used (e.g., Latin, Devanagari, Malayalam, Tamil, Telugu, Kannada, Other).
- `writing_style`: One of `ENGLISH`, `NATIVE_SCRIPT`, `ROMANIZED`, `CODE_MIXED`, or `INFORMAL`.
- `source_type`: One of `REAL`, `SYNTHETIC`, or `AUGMENTED`.

Intent labels (same as project taxonomy)

- PAYMENT_FAILED
- MONEY_DEDUCTED_PAYMENT_FAILED
- PAYMENT_PENDING
- MONEY_DEDUCTED_NO_RECIPIENT
- WRONG_AMOUNT
- DUPLICATE_TRANSACTION
- REFUND_NOT_RECEIVED
- FRAUD_OR_UNAUTHORIZED_TRANSACTION
- QR_PAYMENT_PROBLEM
- UPI_PIN_OR_AUTHENTICATION_PROBLEM
- BANK_ACCOUNT_LINKING_PROBLEM
- UPI_APP_TECHNICAL_PROBLEM
- OTHER_UPI_COMPLAINT

Language categories

- English
- Hindi
- Malayalam
- Tamil
- Telugu
- Kannada
- Other

Writing-style categories

- ENGLISH
- NATIVE_SCRIPT
- ROMANIZED
- CODE_MIXED
- INFORMAL

Illustrative examples — not real customer data:

1)
- complaint_id: EX-0001
- complaint_text: "My UPI payment failed but money was deducted"
- intent: MONEY_DEDUCTED_PAYMENT_FAILED
- language: English
- script: Latin
- writing_style: ENGLISH
- source_type: REAL

2)
- complaint_id: EX-0002
- complaint_text: "mera payment fail ho gya lekin paisa kat gaya"
- intent: MONEY_DEDUCTED_PAYMENT_FAILED
- language: Hindi
- script: Latin
- writing_style: ROMANIZED
- source_type: REAL

3)
- complaint_id: EX-0003
- complaint_text: "ente UPI payment fail ayi, paisa debit aayi"
- intent: MONEY_DEDUCTED_PAYMENT_FAILED
- language: Malayalam
- script: Latin
- writing_style: CODE_MIXED
- source_type: REAL

(These are illustrative examples — not real customer data.)
