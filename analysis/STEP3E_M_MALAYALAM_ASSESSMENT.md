# Step 3E-M: Malayalam Assessment and Integration Planning

Purpose: assess availability of Malayalam datasets/resources and provide a scientifically defensible recommendation for integrating Malayalam into the project without modifying existing validated data (Steps 3A–3E).

Summary recommendation (short):
- Primary recommendation: collect a genuine native-Malayalam customer-support dataset (Option A) for UPI/banking domain via targeted data collection and human annotation; use as primary resource for Malayalam intent experiments.
- Pragmatic interim: create a small, human-annotated Malayalam evaluation/test set (Option C) while planning/collecting a larger native dataset.

Key constraints respected:
- No raw datasets were modified.
- No external datasets were downloaded into `data/raw_data/`.
- This is an assessment/planning step only; no preprocessing, translation, modelling, or augmentation performed.

Candidate resources investigated (high-level):
- AI4Bharat / IndicNLP resources — Indic-language corpora and resources (native Malayalam text, general-domain). Useful for tokenization and language resources; limited domain alignment with customer complaints. (See JSON for source URL and notes.)
- OSCAR / CC-100 (web-crawl filtered corpora) — large-scale Malayalam text from CommonCrawl (native Malayalam), general-domain, licensing varies; useful for tokenizer training but not complaint-specific.
- mC4 (multilingual C4) via TensorFlow Datasets — large-scale web crawl text including Malayalam; general-domain.
- FLORES (parallel translation benchmark) — contains professionally translated test sets including Malayalam (native-script) useful for cross-lingual / translation evaluation but not complaint-specific.
- Samanantar parallel corpus — large English-Indian-language parallel corpora, includes Malayalam-English parallel segments (native script); useful for translation and alignment experiments.
- OPUS / OpenSubtitles / Tatoeba — contain Malayalam sentences (dialogue / conversational), can be mined for examples but domain mismatch and licensing vary.

Romanized Malayalam and code-mixed availability:
- No well-known publicly available Malayalam customer-support datasets in Romanized form were located during this assessment. Romanized Malayalam resources appear rare; most large corpora use native Malayalam script. Code-mixed Malayalam-English corpora exist in niche research contexts but are not standard, and domain-specific (banking/UPI) code-mixed complaint datasets were not found.

Recommended next steps (summary):
1. Plan a targeted native-Malayalam data collection and annotation pipeline for UPI/banking complaint intents (human-in-the-loop annotation). This is the strongest scientific option (Option A) for eventual integration.
2. While collecting, create a small human-annotated Malayalam evaluation set (Option C) to permit initial experiments and comparisons without altering training data.
3. Use language resources (IndicNLP, OSCAR, mC4, FLORES, Samanantar) for tokenizer and language modeling experiments (not for intent labels) and only after careful provenance/licensing review.

See `analysis/step3e_m_malayalam_assessment.json` for structured candidate entries, suitability scores, and a detailed recommendation rationale.
