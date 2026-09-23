# Project Specification

## 1. Project Overview

Project title: Multilingual NLP Framework for Robust Classification of Code-Mixed and Romanized UPI Complaints

This specification documents the problem definition, data schema, research questions, and planned experimental directions. It is Phase 1 project documentation and does not include model implementation or dataset collection.

## 2. Problem Statement

UPI users submit customer complaints in multiple languages and writing styles. Complaints may be written in English, an Indian regional language, Romanized regional language, code-mixed language, or use informal/non-standard spelling. Tokenization and text representation can differ across these forms and may reduce classification robustness.

Research focus: Evaluating and improving the robustness of NLP-based UPI complaint classification under multilingual, code-mixed, Romanized, and informal user-generated text.

## 3. Research Motivation

Financial transaction complaints must be routed and handled quickly. Automated classification helps prioritize and respond. However, multilingual and code-mixed user input presents challenges for tokenization and representation that can harm classification accuracy. This project aims to systematically evaluate these challenges and propose robust processing approaches.

## 4. Input

Primary input: a single customer complaint in natural language.

Examples (illustrative only — not real customer data):

- "My UPI payment failed but money was deducted"
- "mera payment fail ho gya lekin paisa kat gaya"
- "payment failed aayi but amount deduct ayi"
- "ente UPI payment fail ayi, paisa debit aayi"

## 5. Complaint Intent Taxonomy

The initial intent labels (Phase 1 taxonomy) are:

1. PAYMENT_FAILED
2. MONEY_DEDUCTED_PAYMENT_FAILED
3. PAYMENT_PENDING
4. MONEY_DEDUCTED_NO_RECIPIENT
5. WRONG_AMOUNT
6. DUPLICATE_TRANSACTION
7. REFUND_NOT_RECEIVED
8. FRAUD_OR_UNAUTHORIZED_TRANSACTION
9. QR_PAYMENT_PROBLEM
10. UPI_PIN_OR_AUTHENTICATION_PROBLEM
11. BANK_ACCOUNT_LINKING_PROBLEM
12. UPI_APP_TECHNICAL_PROBLEM
13. OTHER_UPI_COMPLAINT

These are initial labels and may be revised after dataset analysis.

## 6. Language and Writing-Style Taxonomy

Language options:

- English
- Hindi
- Malayalam
- Tamil
- Telugu
- Kannada
- Other

Writing style options:

- ENGLISH
- NATIVE_SCRIPT
- ROMANIZED
- CODE_MIXED
- INFORMAL

Note: language and writing_style are distinct fields. For example, `language=Malayalam` and `writing_style=ROMANIZED` is valid.

## 7. Dataset Schema

See `data/schema.md` for full schema and illustrative examples.

## 8. Research Questions

RQ1: How does UPI complaint classification performance vary across English, regional-language, Romanized, and code-mixed complaints?

RQ2: How does tokenization affect the representation of multilingual and code-mixed UPI complaints?

RQ3: Are Romanized and code-mixed complaints significantly harder to classify than standard English or native-script complaints?

RQ4: Can multilingual/subword-based representations improve classification robustness for linguistically diverse UPI complaints?

RQ5: Which complaint categories are most vulnerable to language and tokenization variation?

## 9. Experimental Direction

Planned comparison groups (implementation later):

A. Traditional tokenization
B. Subword-based tokenization
C. Multilingual pretrained tokenization/representation

Evaluation dimensions will include performance across:
- English
- Regional-language native script
- Romanized regional language
- Code-mixed text
- Informal/spelling-variant text

The exact models and tokenizers will be selected in a later phase.

## 10. Planned Workflow Example

An eventual example concept (Phase X): a simple interface where a user enters a complaint (e.g., "mera payment fail ho gya but paisa kat gaya") and the system:

1. Detects/estimates the linguistic form.
2. Normalizes/processes the complaint.
3. Classifies the complaint intent.
4. Displays predicted complaint category and confidence score.
5. Provides a recommended action/response.
6. Shows how the pipeline handled multilingual/code-mixed input.

This is an example concept only; no UI will be built in Phase 1.

## 11. Current Limitations

- No datasets are collected or used at this stage.
- No models or training pipelines are implemented in Phase 1.
- No claims about method superiority or empirical results are made here.

## 12. Future Work

- Dataset collection and annotation consistent with the schema.
- Tokenization and representation experiments.
- Model selection and controlled evaluation across linguistic conditions.
- Prototype walkthrough and user testing.

## 13. Data Strategy and Research Integrity

### Data availability and sourcing

There is no guarantee of access to private UPI or banking complaint records for this project. A large, manually annotated dataset of multilingual, Romanized and code-mixed UPI complaints is unlikely to be publicly available. The project will therefore adopt a controlled and transparent data construction strategy using a combination of:

- Publicly available domain-related text (only when licenses permit research use)
- Public multilingual/code-mixed NLP resources used as auxiliary linguistic references
- Researcher-created base complaints labelled as `RESEARCHER_CREATED` or `SYNTHETIC`
- Human-validated linguistic variants derived from base complaints

All records will include a `source_type` and `source_id` for provenance tracking.

### Data source policy

1. Never scrape private complaint systems or banking portals.
2. Never collect or store transaction numbers, bank account numbers, UPI IDs, phone numbers, OTPs, UPI PINs, card numbers, addresses, or other sensitive financial data.
3. Never use real financial credentials in examples.
4. Researcher-created examples must be explicitly labelled as `RESEARCHER_CREATED` or `SYNTHETIC`.
5. Public datasets may only be used when their license permits research use; record license and source information for every external dataset.
6. Do not download or use any external dataset automatically during Phase 2.

### Focus and scope

The project focuses on linguistic robustness of NLP pipelines for complaint classification, not on transaction-level fraud detection or financial processing. Auxiliary linguistic resources (e.g., COMI-LINGUA) may be used for code-mixing analysis but are not a substitute for UPI complaint data.

### Provenance and privacy

Record `source_id` and license information for all external data. Annotators must use anonymized IDs. Redact any sensitive information discovered in raw text and record the redaction event in provenance metadata.

### Experimental control and leakage prevention

All linguistic variants derived from a single base complaint must remain in the same data partition (train/validation/test). Splits must be performed at the base-complaint level to prevent leakage of near-duplicate semantic content across partitions.


