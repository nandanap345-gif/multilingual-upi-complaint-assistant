# DATA CARD

1. Dataset name

Multilingual UPI Complaint Robustness Dataset (planned)

2. Purpose

Research on multilingual and code-mixed robustness for UPI complaint classification.

3. Intended use

- Academic research and benchmarking of multilingual tokenization and classification robustness.

4. Out-of-scope use

- Fraud detection that requires transaction-level metadata.
- Any use that requires or exposes sensitive financial identifiers.

5. Data sources

- Publicly available domain-related text (subject to licensing)
- Public multilingual/code-mixed NLP resources (as auxiliary references)
- Researcher-created examples (labelled `RESEARCHER_CREATED`)
- Human-validated linguistic variants

6. Data creation method

Controlled researcher-created base complaints with human-validated linguistic variants.

7. Language coverage

English, Hindi, Malayalam, Tamil, Telugu, Kannada, and Others (as documented).

8. Intent categories

See project taxonomy in docs/project_specification.md.

9. Annotation process

Annotators assign intent, language, script, writing_style. Validation records `annotator_id` and `validation_status`.

10. Quality control

Human validation by annotators fluent in the relevant language; record validation status and reviewer notes.

11. Privacy considerations

- No transaction identifiers, UPI IDs, phone numbers, PINs, OTPs, card numbers, or bank account numbers are to be stored.
- Researcher-created examples must be synthetic and clearly labelled as such.

12. Licensing considerations

External public datasets may only be used if their licenses permit research use; record license and source_id for provenance.

13. Known limitations

- Initial dataset will be limited in size and scope; not representative of complete real-world distribution.

14. Potential biases

- Language coverage, dialect variety, and demographic representation may be uneven; report and document coverage.

15. Train/validation/test splitting strategy

- Split at base-complaint level to prevent leakage across linguistic variants. Keep all variants of a base complaint in the same partition.

Statement

The initial dataset is intended for research on multilingual NLP robustness in UPI complaint classification and is not a dataset of actual banking transactions.
