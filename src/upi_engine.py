"""Explainable, privacy-aware routing for UPI complaints.

This module deliberately uses transparent rules for the UPI-specific result.
The bundled ML model is trained on BANKING77 (a broad banking dataset), so it
is used separately as a research baseline and is never represented as a
UPI-trained production model.
"""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import joblib


UPI_INTENTS: Dict[str, Dict[str, object]] = {
    "FRAUD_OR_UNAUTHORIZED_TRANSACTION": {
        "title": "Unrecognized or unauthorized UPI transaction",
        "severity": "High",
        "keywords": ("not me", "didn't make", "did not make", "unauthorised", "unauthorized", "fraud", "scam", "unknown transaction", "someone sent", "someone transferred", "maine nahi", "मैंने नहीं"),
        "steps": ("Contact your bank or UPI app through its official support channel immediately.", "Use the app or bank’s official process to report the unauthorized transaction.", "Do not share your PIN, OTP, or device screen with anyone."),
    },
    "UPI_PIN_OR_AUTHENTICATION_PROBLEM": {
        "title": "UPI PIN or authentication problem",
        "severity": "Medium",
        "keywords": ("upi pin", "forgot pin", "reset pin", "wrong pin", "authentication", "otp", "verify", "verification failed", "पिन"),
        "steps": ("Use only the official UPI app to reset or verify your UPI PIN.", "Never disclose a UPI PIN or OTP; genuine support staff will not ask for it.", "If verification keeps failing, contact your bank’s official support."),
    },
    "MONEY_DEDUCTED_PAYMENT_FAILED": {
        "title": "Payment failed but money was debited",
        "severity": "Medium",
        "keywords": ("money deducted", "amount deducted", "amount debited", "money debited", "paisa kat", "paise kat", "पैसे कट", "debit aayi", "debited but", "deducted but"),
        "steps": ("Check the transaction status in your UPI app and bank statement.", "Allow the normal reversal window stated by your bank or UPI provider.", "If it is not reversed, raise a complaint with the transaction reference in the official app."),
    },
    "PAYMENT_PENDING": {
        "title": "UPI payment pending",
        "severity": "Medium",
        "keywords": ("pending", "processing", "still waiting", "in progress", "awaiting"),
        "steps": ("Do not send the payment again until the first transaction is resolved.", "Check the transaction status in the UPI app.", "If it remains pending beyond your provider’s stated window, use official in-app support."),
    },
    "MONEY_DEDUCTED_NO_RECIPIENT": {
        "title": "Money debited but recipient has not received it",
        "severity": "Medium",
        "keywords": ("recipient not received", "receiver not received", "beneficiary not received", "not received by recipient", "receiver didn't get", "recipient didn't get", "paise nahi mile", "पैसे नहीं मिले"),
        "steps": ("Confirm the recipient’s UPI ID and ask them to check their transaction history.", "Check whether the transaction is marked successful, pending, or failed.", "If it is successful but unresolved, file a complaint through the official UPI app with the reference number."),
    },
    "REFUND_NOT_RECEIVED": {
        "title": "UPI refund not received",
        "severity": "Medium",
        "keywords": ("refund", "reversal not received", "reversed amount", "return money", "money back"),
        "steps": ("Check the merchant’s refund confirmation and the expected refund time.", "Review your bank statement, not only the app balance.", "If the stated refund period has passed, contact the merchant and then official UPI or bank support."),
    },
    "DUPLICATE_TRANSACTION": {
        "title": "Duplicate UPI transaction",
        "severity": "Medium",
        "keywords": ("duplicate", "twice", "two times", "double charged", "charged twice", "again debited"),
        "steps": ("Check whether both transaction references are distinct and successful.", "Do not delete transaction records or receipts.", "Report the duplicate charge through the official app or bank support."),
    },
    "WRONG_AMOUNT": {
        "title": "Incorrect UPI transaction amount",
        "severity": "Medium",
        "keywords": ("wrong amount", "incorrect amount", "extra amount", "more than", "less than", "charged extra"),
        "steps": ("Compare the app receipt with the intended amount and any merchant bill.", "Keep the transaction reference and receipt ready.", "Raise the discrepancy through the official merchant, UPI app, or bank support channel."),
    },
    "WRONG_RECIPIENT": {
        "title": "Money sent to the wrong UPI ID",
        "severity": "High",
        "keywords": ("wrong upi", "wrong recipient", "wrong person", "sent by mistake", "sent to wrong", "गलत upi", "गलत व्यक्ति"),
        "steps": ("Contact your bank or UPI provider immediately using its official complaint process.", "Keep the transaction reference, date, and amount ready.", "A transfer cannot always be reversed automatically; avoid contacting unknown parties with sensitive information."),
    },
    "QR_PAYMENT_PROBLEM": {
        "title": "QR-code payment problem",
        "severity": "Low",
        "keywords": ("qr", "scan code", "scanner", "barcode"),
        "steps": ("Check that the QR code belongs to the intended merchant or person.", "Update the UPI app and try a stable internet connection.", "If you were charged but the payment did not complete, use the transaction-specific support option."),
    },
    "BANK_ACCOUNT_LINKING_PROBLEM": {
        "title": "Bank-account linking problem",
        "severity": "Low",
        "keywords": ("link bank", "bank account link", "add bank", "account not showing", "account linking"),
        "steps": ("Confirm that the mobile number registered with the bank is active on this phone.", "Ensure SMS permissions are enabled for the official UPI app.", "If the account still does not appear, contact your bank’s official support."),
    },
    "UPI_APP_TECHNICAL_PROBLEM": {
        "title": "UPI app or network problem",
        "severity": "Low",
        "keywords": ("app crash", "app not working", "technical error", "server error", "network error", "unable to open", "something went wrong"),
        "steps": ("Check your network connection and update the official UPI app.", "Restart the app; do not repeatedly retry a transaction that may be pending.", "Contact official app support if the issue persists."),
    },
    "UPI_TRANSACTION_LIMIT": {
        "title": "UPI transaction-limit problem",
        "severity": "Low",
        "keywords": ("limit exceeded", "daily limit", "transaction limit", "limit reached", "maximum limit"),
        "steps": ("Check your bank’s and UPI app’s current transaction limits.", "Do not attempt repeated transactions if the limit has been reached.", "Contact your bank if the displayed limit seems incorrect."),
    },
    "PAYMENT_FAILED": {
        "title": "UPI payment failed",
        "severity": "Medium",
        "keywords": ("payment failed", "upi failed", "transaction failed", "declined", "failure", "fail ho", "failed aayi", "विफल"),
        "steps": ("Check your internet connection, account balance, and UPI app status.", "Do not retry immediately if the first transaction may still be processing.", "Use official in-app support if the failure continues."),
    },
    "OTHER_UPI_COMPLAINT": {
        "title": "UPI issue needs clarification",
        "severity": "Low",
        "keywords": (),
        "steps": ("Add whether the payment failed, is pending, was debited, or reached the wrong recipient.", "Do not share a UPI PIN, OTP, or full account number.", "Use the official UPI-app or bank support channel if the transaction is urgent."),
    },
}

MALAYALAM_SIGNAL_PHRASES: Dict[str, Tuple[str, ...]] = {
    "MONEY_DEDUCTED_PAYMENT_FAILED": (
        "പണം ഡെബിറ്റ് ആയി",
        "പേയ്‌മെന്റ് പരാജയപ്പെട്ടു",
        "പേയ്മെന്റ് പരാജയപ്പെട്ടു",
        "പണം പോയി പക്ഷേ പേയ്‌മെന്റ് പരാജയപ്പെട്ടു",
        "പണം പോയി പക്ഷേ പേയ്മെന്റ് പരാജയപ്പെട്ടു",
        "ട്രാൻസ്ഫർ ചെയ്തു പക്ഷേ പേയ്‌മെന്റ് പരാജയപ്പെട്ടു",
        "ട്രാൻസ്ഫർ ചെയ്തു പക്ഷേ പേയ്മെന്റ് പരാജയപ്പെട്ടു",
    ),
    "MONEY_DEDUCTED_NO_RECIPIENT": (
        "ട്രാൻസ്ഫർ ചെയ്തു പക്ഷേ എത്തിയില്ല",
        "ട്രാൻസ്ഫർ ചെയ്തു പക്ഷേ ലഭിച്ചില്ല",
        "പണം ട്രാൻസ്ഫർ ചെയ്തു പക്ഷേ ലഭിച്ചില്ല",
        "പണം പോയി പക്ഷേ കിട്ടിയില്ല",
        "എത്തിയില്ല",
        "എത്തിില്ല",
        "അവിടെ എത്തിയില്ല",
        "ലഭിച്ചില്ല",
        "കിട്ടിയില്ല",
    ),
    "WRONG_RECIPIENT": (
        "തെറ്റായ യുപിഐ",
        "തെറ്റായ ആളിന് അയച്ചു",
        "തെറ്റായി അയച്ചു",
        "തെറ്റായ നമ്പറിലേക്ക് അയച്ചു",
        "തെറ്റായ അക്കൗണ്ടിലേക്ക് അയച്ചു",
        "തെറ്റായ വ്യക്തിക്ക് അയച്ചു",
    ),
    "REFUND_NOT_RECEIVED": (
        "റിഫണ്ട് ലഭിച്ചില്ല",
        "റീഫണ്ട് വന്നില്ല",
        "പണം തിരികെ കിട്ടിയില്ല",
        "തിരികെ വന്നില്ല",
        "റിഫണ്ട് കിട്ടിയില്ല",
    ),
    "PAYMENT_FAILED": (
        "പേയ്മെന്റ് പരാജയപ്പെട്ടു",
        "ഡെബിറ്റ് ആയി പക്ഷേ പേയ്മെന്റ് പരാജയപ്പെട്ടു",
        "പണം പോയി പക്ഷേ പേയ്മെന്റ് പരാജയപ്പെട്ടു",
        "പേയ്മെന്റ് വിഫലമായി",
    ),
}

SENSITIVE_PATTERNS: Tuple[Tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b\d{6}\b"), "[6-digit number hidden]"),
    (re.compile(r"\b\d{10,18}\b"), "[long number hidden]"),
    (re.compile(r"\b[\w.+-]{2,}@[\w-]{2,}\b", re.IGNORECASE), "[UPI ID hidden]"),
)

FOLLOW_UP_QUESTIONS: Dict[str, Tuple[Tuple[str, str, Tuple[str, ...]], ...]] = {
    "MONEY_DEDUCTED_PAYMENT_FAILED": (("status", "What status does the UPI app show?", ("Failed", "Pending", "Successful", "Not sure")), ("reversed", "Has the debited amount been reversed?", ("Yes", "No", "Not sure"))),
    "PAYMENT_PENDING": (("pending_time", "How long has it been pending?", ("Less than 30 minutes", "30 minutes to 24 hours", "More than 24 hours", "Not sure")), ("retry", "Have you tried sending the payment again?", ("No", "Yes", "Not sure"))),
    "MONEY_DEDUCTED_NO_RECIPIENT": (("status", "What status does the UPI app show?", ("Successful", "Pending", "Failed", "Not sure")), ("recipient_check", "Has the recipient checked their transaction history?", ("Yes", "No", "Not sure"))),
    "FRAUD_OR_UNAUTHORIZED_TRANSACTION": (("recognized", "Do you recognize this transaction?", ("No, I do not recognize it", "I am not sure", "Yes, I recognize it")), ("app_access", "Do you still have access to your UPI app?", ("Yes", "No", "Not sure"))),
    "REFUND_NOT_RECEIVED": (("refund_time", "How long ago was the refund initiated?", ("Less than 24 hours", "1 to 5 days", "More than 5 days", "Not sure")),),
    "PAYMENT_FAILED": (("debited", "Was money debited from your account?", ("Yes", "No", "Not sure")), ("retry", "Have you retried the payment?", ("No", "Yes", "Not sure"))),
}

STOP_WORDS = {"a", "an", "and", "are", "but", "for", "from", "i", "in", "is", "it", "my", "of", "on", "or", "please", "the", "this", "to", "up", "upi", "was", "with"}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPI_ROUTER_MODEL_PATH = os.path.join(ROOT, "models", "upi_router_char_logreg.joblib")


@dataclass(frozen=True)
class AnalysisResult:
    language: str
    writing_style: str
    sanitized_text: str
    privacy_flags: List[str]
    primary_intent: str
    title: str
    severity: str
    confidence_label: str
    confidence_score: int
    clarification: str
    next_steps: Tuple[str, ...]
    top_matches: List[Tuple[str, str, int]]
    matched_signals: List[str]


def normalize_text(text: str) -> str:
    """Conservative normalisation that preserves the meaning and script."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(text or ""))).strip()


def sanitize_text(text: str) -> Tuple[str, List[str]]:
    sanitized = text
    flags: List[str] = []
    for pattern, replacement in SENSITIVE_PATTERNS:
        if pattern.search(sanitized):
            sanitized = pattern.sub(replacement, sanitized)
            flags.append(replacement.strip("[]"))
    if re.search(r"\b(?:upi\s*)?pin\s*(?:is|:)?\s*\d+\b", text, re.IGNORECASE):
        flags.append("Possible UPI PIN")
    return sanitized, list(dict.fromkeys(flags))


def extract_key_terms(text: str, limit: int = 8) -> List[str]:
    """Expose lightweight lexical features for the NLP process."""
    safe_text, _ = sanitize_text(normalize_text(text).lower())
    terms = re.findall(r"[a-zA-Z]{3,}|[\u0900-\u0D7F]{2,}", safe_text)
    return list(dict.fromkeys(term for term in terms if term not in STOP_WORDS))[:limit]


@lru_cache(maxsize=1)
def load_router_model():
    if not os.path.exists(UPI_ROUTER_MODEL_PATH):
        return None
    try:
        return joblib.load(UPI_ROUTER_MODEL_PATH)
    except Exception:
        return None


def predict_router_intent(text: str) -> Tuple[Optional[str], float]:
    model = load_router_model()
    if model is None:
        return None, 0.0
    try:
        normalized = normalize_text(text)
        probabilities = model.predict_proba([normalized])[0]
        classifier = model.named_steps.get("clf") if hasattr(model, "named_steps") else model
        classes = getattr(classifier, "classes_", None)
        if classes is None or len(classes) == 0:
            return None, 0.0
        best_index = max(range(len(probabilities)), key=lambda index: probabilities[index])
        return str(classes[best_index]), float(probabilities[best_index])
    except Exception:
        return None, 0.0


def get_follow_up_questions(intent: str) -> Tuple[Tuple[str, str, Tuple[str, ...]], ...]:
    """Return only questions that help distinguish the detected UPI issue."""
    return FOLLOW_UP_QUESTIONS.get(intent, ())


def detect_language(text: str) -> Tuple[str, str]:
    if re.search(r"[\u0D00-\u0D7F]", text):
        return "Malayalam", "NATIVE_SCRIPT"
    if re.search(r"[\u0900-\u097F]", text):
        return "Hindi", "NATIVE_SCRIPT"
    if re.search(r"[\u0B80-\u0BFF]", text):
        return "Tamil", "NATIVE_SCRIPT"
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "Telugu", "NATIVE_SCRIPT"
    if re.search(r"[\u0C80-\u0CFF]", text):
        return "Kannada", "NATIVE_SCRIPT"
    words = set(re.findall(r"[a-z]+", text.lower()))
    hinglish = {"mera", "meri", "mujhe", "paisa", "paise", "nahi", "nahi", "hua", "gaya", "gayi", "kyu", "kyun", "kya", "hai", "kat"}
    malayalam_romanized = {"ente", "paisa", "ayi", "illa", "poyi", "payment", "debit"}
    if len(words & hinglish) >= 2:
        return "Hinglish", "ROMANIZED"
    if len(words & malayalam_romanized) >= 2:
        return "Romanized Malayalam", "ROMANIZED"
    return "English", "ENGLISH"


def _score_intents(text: str) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    lowered = text.lower()
    scores: Dict[str, int] = {intent: 0 for intent in UPI_INTENTS}
    signals: Dict[str, List[str]] = {intent: [] for intent in UPI_INTENTS}
    for intent, details in UPI_INTENTS.items():
        for keyword in details["keywords"]:  # type: ignore[index]
            if keyword.lower() in lowered:
                weight = 3 if " " in keyword else 2
                scores[intent] += weight
                signals[intent].append(keyword)

    # Native-script equivalents used in the included Malayalam sample.
    if "\u0d21\u0d46\u0d2c\u0d3f\u0d31\u0d4d" in lowered:  # "debit"
        scores["MONEY_DEDUCTED_PAYMENT_FAILED"] += 2
        signals["MONEY_DEDUCTED_PAYMENT_FAILED"].append("Malayalam debit signal")
    if "\u0d2a\u0d30\u0d3e\u0d1c\u0d2f" in lowered:  # "failure"
        scores["PAYMENT_FAILED"] += 2
        signals["PAYMENT_FAILED"].append("Malayalam failure signal")
    for intent, phrases in MALAYALAM_SIGNAL_PHRASES.items():
        for phrase in phrases:
            if phrase in text:
                scores[intent] += 4
                signals[intent].append(f"Malayalam phrase: {phrase}")

    if "money was deducted" in lowered:
        scores["MONEY_DEDUCTED_PAYMENT_FAILED"] += 2
        signals["MONEY_DEDUCTED_PAYMENT_FAILED"].append("English debited phrase")
    if "റിഫണ്ട്" in text and "വന്നില്ല" in text:
        scores["REFUND_NOT_RECEIVED"] += 3
        signals["REFUND_NOT_RECEIVED"].append("Malayalam refund + not received pattern")
    if any(marker in text for marker in ("\u0d2a\u0d46\u0d28\u0d4d\u0d21\u0d3f\u0d19\u0d4d", "\u0d2a\u0d46\u0d1f\u0d4d\u0d21\u0d3f\u0d19\u0d4d", "\u0d2a\u0d46\u0d28\u0d4d\u0d21\u0d3f\u0d19\u0d4d\u0d17\u0d4d")) and any(marker in text for marker in ("\u0d2a\u0d3e\u0d07\u0d38", "\u0d2a\u0d4b\u0d2f\u0d3f", "\u0d21\u0d46\u0d2c\u0d3f\u0d31\u0d4d\u0d31\u0d4d")):
        scores["PAYMENT_PENDING"] += 5
        signals["PAYMENT_PENDING"].append("Malayalam pending + money moved signal")

    # Context matters: a debit plus failure is more specific than either alone.
    has_debit = scores["MONEY_DEDUCTED_PAYMENT_FAILED"] > 0
    has_failure = scores["PAYMENT_FAILED"] > 0
    if has_debit and has_failure:
        scores["MONEY_DEDUCTED_PAYMENT_FAILED"] += 5
        signals["MONEY_DEDUCTED_PAYMENT_FAILED"].append("debit + failed context")
    if scores["MONEY_DEDUCTED_NO_RECIPIENT"] > 0 and has_debit:
        scores["MONEY_DEDUCTED_NO_RECIPIENT"] += 3
    return scores, signals


def _clarification_for(intent: str) -> str:
    questions = {
        "MONEY_DEDUCTED_PAYMENT_FAILED": "Was the transaction marked failed, and has the amount already been reversed?",
        "PAYMENT_PENDING": "Is the transaction currently shown as pending in the UPI app?",
        "MONEY_DEDUCTED_NO_RECIPIENT": "Does the recipient’s transaction history show that the money was not received?",
        "PAYMENT_FAILED": "Was any amount debited from your account?",
        "FRAUD_OR_UNAUTHORIZED_TRANSACTION": "Was this transaction made by someone other than you?",
    }
    return questions.get(intent, "Please select the closest issue below or add the transaction status for a more precise result.")


def analyse_complaint(text: str, manual_language: str = "Auto detect") -> AnalysisResult:
    clean = normalize_text(text)
    sanitized, privacy_flags = sanitize_text(clean)
    detected_language, writing_style = detect_language(clean)
    language = detected_language if manual_language == "Auto detect" else manual_language
    scores, signals = _score_intents(clean)
    ranked = sorted(scores, key=lambda item: scores[item], reverse=True)
    top = ranked[0]
    top_score = scores[top]
    second_score = scores[ranked[1]]

    if top_score == 0:
        top = "OTHER_UPI_COMPLAINT"
        confidence_score, confidence_label = 20, "Low"
        clarification = "Could you say whether the payment failed, is pending, was debited, or was sent to the wrong recipient?"
    else:
        confidence_score = min(95, 35 + top_score * 10 + max(0, top_score - second_score) * 5)
        confidence_label = "High" if confidence_score >= 75 else "Medium" if confidence_score >= 55 else "Low"
        clarification = "" if confidence_label != "Low" else _clarification_for(top)

    ml_intent, ml_confidence = predict_router_intent(clean)
    if ml_intent in UPI_INTENTS and (top == "OTHER_UPI_COMPLAINT" or confidence_label == "Low"):
        top = ml_intent
        details = UPI_INTENTS[top]
        confidence_score = max(confidence_score, min(95, int(30 + ml_confidence * 70)))
        confidence_label = "High" if ml_confidence >= 0.75 else "Medium" if ml_confidence >= 0.45 else "Low"
        clarification = "" if confidence_label != "Low" else _clarification_for(top)
        signals[top].append(f"ML fallback: {ml_confidence:.2f}")

    details = UPI_INTENTS[top]
    matches = [(intent, str(UPI_INTENTS[intent]["title"]), scores[intent]) for intent in ranked[:3] if scores[intent] > 0]
    if not matches:
        matches = [(top, str(details["title"]), 0)]
    return AnalysisResult(
        language=language,
        writing_style=writing_style,
        sanitized_text=sanitized,
        privacy_flags=privacy_flags,
        primary_intent=top,
        title=str(details["title"]),
        severity=str(details["severity"]),
        confidence_label=confidence_label,
        confidence_score=confidence_score,
        clarification=clarification,
        next_steps=tuple(details["steps"]),  # type: ignore[arg-type]
        top_matches=matches,
        matched_signals=signals[top],
    )


def build_complaint_summary(result: AnalysisResult) -> str:
    """Return a copyable summary that intentionally excludes sensitive values."""
    return (
        f"Subject: UPI complaint – {result.title}\n\n"
        f"Issue category: {result.primary_intent}\n"
        f"Language detected: {result.language}\n"
        f"Complaint: {result.sanitized_text}\n\n"
        "Please help me review this transaction and advise me on the official resolution process. "
        "I can provide the transaction reference through the official support channel if required."
    )


def build_structured_summary(result: AnalysisResult, answers: Dict[str, str]) -> str:
    """Create a safe, copyable support summary from NLP output and form answers."""
    selected_answers = {key.replace("_", " ").title(): value for key, value in answers.items() if value and value not in {"Not sure", "I am not sure"}}
    answer_block = "".join(f"- {label}: {value}\n" for label, value in selected_answers.items())
    details = f"\nAdditional details:\n{answer_block}" if answer_block else ""
    return (
        f"Subject: UPI complaint - {result.title}\n\n"
        f"Issue category: {result.primary_intent}\n"
        f"Language detected: {result.language}\n"
        f"Complaint: {result.sanitized_text}\n{details}\n"
        "Please review this transaction and advise me through the official resolution process. "
        "I can provide the transaction reference only through the official support channel if required."
    )


def personalised_guidance(result: AnalysisResult, answers: Dict[str, str]) -> str:
    """Add a deterministic recommendation based on the relevant follow-up answers."""
    if result.primary_intent == "MONEY_DEDUCTED_PAYMENT_FAILED" and answers.get("reversed") == "No":
        return "Because the amount has not been reversed, keep the transaction reference ready and use the official in-app dispute option after the provider's stated reversal window."
    if result.primary_intent == "PAYMENT_PENDING" and answers.get("pending_time") == "More than 24 hours":
        return "A payment pending for more than 24 hours should be escalated through official UPI-app or bank support. Do not send the payment again."
    if result.primary_intent == "PAYMENT_FAILED" and answers.get("debited") == "Yes":
        return "Since money was debited, treat this as a possible reversal issue and check the status before making another payment."
    if result.primary_intent == "FRAUD_OR_UNAUTHORIZED_TRANSACTION" and answers.get("recognized") == "No, I do not recognize it":
        return "Treat this as urgent: report it through an official bank or UPI-app channel immediately and do not share OTPs or PINs with anyone."
    return "Your selected details have been included in the structured complaint summary for official support."
