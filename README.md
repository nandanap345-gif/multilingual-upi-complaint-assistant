# UPI Complaint Intelligence

An accessible Streamlit app for explainable, multilingual routing of common UPI complaints. It is designed to show how financial-support text can be handled when it is informal, code-mixed, Romanized, or written in Indian scripts.

## What the app does

- Routes a complaint to one of 15 UPI-focused issue categories, including failed-but-debited payments, pending payments, fraud, refunds, QR issues, and PIN problems.
- Detects English, Hindi, Malayalam, Tamil, Telugu, Kannada, Hinglish, and some Romanized Malayalam signals.
- Displays a clear urgency level, next steps, alternative matches, and an explainable list of matched signals.
- Hides likely UPI IDs and long numeric values in its generated complaint summary.
- Includes one-click English, Hinglish, Malayalam, and fraud sample inputs.
- Supports optional English, Hinglish, and Hindi voice recording with speech-to-text; typed input remains available when transcription is unavailable.
- Includes a locally saved support-agent dashboard with masked ticket history, priority counts, language counts, and a ticket queue.
- Shows recorded BANKING77 model results and, when local model files are present, the model prediction as a clearly labelled research baseline.

## Important design note

The included TF-IDF + Linear SVM model was trained on **BANKING77**, a broad banking-support dataset with 77 intents. It is not presented as a UPI-specific production model. The visible UPI result comes from the transparent, UPI-specific routing logic in `src/upi_engine.py`; the BANKING77 model is retained for research comparison.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Test the routing logic

```powershell
pytest tests/test_upi_engine.py -q
```

## Project structure

- `app.py` — Streamlit interface.
- `src/upi_engine.py` — testable language detection, privacy filtering, intent routing, confidence, and complaint-summary logic.
- `tests/test_upi_engine.py` — focused tests for core flows.
- `models/` — existing BANKING77 baseline model and vectorizer.
- `analysis/` — experiment reports and comparison artifacts.

## Safety and scope

This is an educational prototype. It does not file complaints, access bank accounts, or make financial decisions. Users should never share a UPI PIN, OTP, CVV, or full account/card number. For fraud or transaction disputes, users must use verified official bank, NPCI, or UPI-provider support channels.

Voice transcription is optional. When the user explicitly presses **Transcribe recording**, the recorded clip is sent to Google Speech Recognition. Do not use it for sensitive information; typed input is always available.

The dashboard saves only masked ticket fields to `data/ticket_history.json` on the local machine. The generated file is ignored by Git and can be cleared from the dashboard.

## Suggested walkthrough

1. Press **Hinglish** or **Malayalam** sample.
2. Show language detection and the explainable UPI route.
3. Point out the action checklist and generated safe summary.
4. Run the fraud sample and show the high-urgency safety message.
5. Open **Model insights** to explain the model comparison and the distinction between the research baseline and the UPI router.
