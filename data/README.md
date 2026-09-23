# Data Directory README

This folder explains how data is organized and handled for the project.

raw/
- Contains original, unmodified source files. Only headers or provenance records should be committed here; raw files with actual customer data must never be stored in the repository.

processed/
- Contains cleaned, transformed, or normalized data used for experiments. Processed data must reference the original `source_id` and must never contain sensitive financial identifiers.

test/
- Holds small, controlled test files used for unit tests and pipeline verification. Do not store real customer data here.

Provenance and tracking

- For every external source, record `source_type`, `source_id`, and license information in a provenance ledger (external to this repo or in a controlled file in `data/`).
- Annotator IDs should be anonymized (e.g., `ann-001`) and not include full names.

Privacy

- Do not store UPI IDs, bank account numbers, phone numbers, OTPs, PINs, or other financial identifiers in the repository.
- If a raw text contains sensitive information, redact before storing and record the redaction in provenance metadata.

Data modification policy

- Raw files must not be silently modified. Any normalization must be stored in `processed/` with clear links to the raw `source_id`.

