# Step 3F — Dataset & Language Scope Freeze

Objective
---------
Produce a final, auditable freeze of the datasets and language scope to be used for downstream experiments. No preprocessing, translation, tokenization, augmentation, or modeling was performed as part of this step.

Summary of primary datasets
---------------------------

A. Primary dataset — BANKING77
- Files: `data/raw_data/banking77_train.csv`, `data/raw_data/banking77_test.csv`
- Train rows: 10,003
- Test rows: 3,080
- Combined: 13,083
- Intent categories: 77 unique `category` labels across train+test
- Structure: CSV with columns `text,category` (text is the user utterance; category is the intent label)
- Why suitable: domain-specific banking/financial intent dataset, curated into 77 granular intents that align with the project's intent-classification objective.

B. Multilingual/customer-support resource — karanverma19_multilingual_customer_support_intent_dataset
- File: `data/raw_data/karanverma19_multilingual_customer_support_intent_dataset.csv`
- Total records: 41
- Columns: `query,intent,language,category`
- Languages present (source labels): Hindi, Hinglish, Punjabi, English
- What it can support: small-scale cross-lingual examples and exploratory checks for multilingual heuristics; useful for qualitative tests and rule-based heuristics.
- What it cannot support: robust training for additional languages (too small), nor comprehensive evaluation across intents.

C. Romanized / code-mixed language scope (observed and exploratory)
- Languages observed in karanverma19 and exploratory Step 3E outputs: Hindi, Hinglish (romanized Hindi), Punjabi, English
- Distinguish source-provided labels vs exploratory labels: the `language` column in `karanverma19` is source-provided; exploratory labels in `analysis/step3e_results.json` and `STEP3E_ROMANIZED_CODEMIX_REPORT.md` are manual/heuristic assessments and are explicitly NOT gold-standard linguistic annotations.

D. Malayalam (explicit inclusion)
- Verified Malayalam resources (sample-level verification completed in Step 3E-M3):
  - Zenodo: "A Sentiment Analysis Dataset for Code-Mixed Malayalam-English" (DOI: 10.5281/zenodo.4015234) — previewed; Romanized Malayalam and code-mixing observed; license CC-BY-4.0. Suitable for code-mixing evaluation, not direct intent training.
  - Hugging Face: `anjalikrishna07/hospitalcall_malayalam` — previewed; native-script Malayalam transcripts observed (call-center/hospital domain); license not programmatically confirmed — verify dataset card before reuse.
- Resources identified via metadata (but not fully verified or unsuitable for direct use): large corpora (OSCAR, mC4, Samanantar) — contain Malayalam content but are not complaint-specific; license/usage varies.
- Resources not suitable for direct inclusion without relabeling or additional collection: Zenodo (sentiment labels) — different label taxonomy; Hugging Face (call transcripts) — healthcare domain, lacks intent labels for banking/UPI.
- Can Malayalam be included in the current experiment without translation/additional collection? No. Existing verified Malayalam resources are not directly compatible with BANKING77's intent taxonomy. Do NOT translate BANKING77 or fabricate Malayalam examples at this stage.

E. Data integrity guarantees
- Original raw datasets remain untouched: `data/raw_data/*` files were not modified by any step.
- No translation, transliteration, augmentation, tokenization, or preprocessing applied in any step so far.
- No model training, embedding generation, or model artifacts were created.

Final language-scope table
-------------------------
Language | Script/Form | Dataset/Resource | Directly Available? | Verified? | Suitable for Current Experiment? | Notes
-|-|-|-|-|-|-
English | Latin | BANKING77 | Yes | Yes | Yes | Primary intent dataset (77 intents)
Hindi | Devanagari / Romanized (Hinglish) | karanverma19 | Yes | Yes (small) | No (too small) | Source-provided `language` labels; exploratory romanized tags exist
Hinglish | Romanized | karanverma19 + step3e | Yes | Yes (exploratory) | No | Romanized forms present; labels exploratory
Punjabi | Gurmukhi / Romanized | karanverma19 | Yes | Yes (small) | No | Small sample size
Malayalam | Malayalam script / Romanized | Zenodo (code-mix), HuggingFace (hospitalcall) | Partially | Yes (previewed) | No (not directly) | Verified previews; not intent-labelled for banking

Final dataset-scope table
------------------------
Dataset/resource | Purpose | Records | Labels/Intents | Language coverage | Current status | Recommended use
-|-|-|-|-|-|-
BANKING77 | Primary intent classification | 13,083 | 77 intent categories | English | Verified, raw kept | Train/test primary
karanverma19 | Multilingual customer-support examples | 41 | intent | Hindi/Hinglish/Punjabi/English | Verified | Qualitative evaluation / heuristics
Zenodo (code-mix) | Code-mixed Malayalam-English sentiment | unknown (TSV ~498KB) | sentiment labels | Malayalam (romanized)/English | Previewed | Evaluation / code-mixing analyses (B/C)
hospitalcall_malayalam | Call transcripts (healthcare) | ~8.97k | transcript/audio metadata | Malayalam (native-script) | Previewed; license unverified | Evaluation, tokenization, representation (B/C)

OBSERVED FACTS
--------------
- BANKING77 is the project's primary, verified intent dataset (13,083 records, 77 intents).
- karanverma19 contains 41 multilingual customer-support queries with `language` labels.
- Zenodo and Hugging Face Malayalam resources were previewed; Zenodo shows Romanized Malayalam and code-mixing; Hugging Face shows native-script Malayalam transcripts.

VERIFIED RESOURCES
------------------
- BANKING77 (raw CSVs) — verified and untouched
- karanverma19 — verified and untouched
- Zenodo (10.5281/zenodo.4015234) — preview verified; license CC-BY-4.0
- Hugging Face hospitalcall_malayalam — preview verified; license must be confirmed manually

EXPLORATORY OBSERVATIONS
------------------------
- Per-record romanized/code-mixed tagging in `analysis/step3e_results.json` and reports are exploratory heuristics and manual assessments; they are not gold-standard annotations.

LIMITATIONS
-----------
- Malayalam resources verified are not directly compatible with BANKING77 intent taxonomy.
- karanverma19 is too small for training.
- License for Hugging Face dataset must be explicitly checked before reuse.

DECISIONS FOR NEXT STAGE
------------------------
- Modeling not allowed until a formal decision to include new data is made.
- Recommended safer option for Malayalam: collect or annotate a dedicated Malayalam customer-support/intent dataset (Option A from Step 3E-M assessment), or create a small human-annotated evaluation set (Option C), rather than translating existing datasets.
