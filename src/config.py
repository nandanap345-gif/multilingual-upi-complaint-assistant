# Project constants for Phase 1 — Problem Definition and Data Specification

INTENT_LABELS = [
    "PAYMENT_FAILED",
    "MONEY_DEDUCTED_PAYMENT_FAILED",
    "PAYMENT_PENDING",
    "MONEY_DEDUCTED_NO_RECIPIENT",
    "WRONG_AMOUNT",
    "DUPLICATE_TRANSACTION",
    "REFUND_NOT_RECEIVED",
    "FRAUD_OR_UNAUTHORIZED_TRANSACTION",
    "QR_PAYMENT_PROBLEM",
    "UPI_PIN_OR_AUTHENTICATION_PROBLEM",
    "BANK_ACCOUNT_LINKING_PROBLEM",
    "UPI_APP_TECHNICAL_PROBLEM",
    "OTHER_UPI_COMPLAINT",
]

LANGUAGES = [
    "English",
    "Hindi",
    "Malayalam",
    "Tamil",
    "Telugu",
    "Kannada",
    "Other",
]

WRITING_STYLES = [
    "ENGLISH",
    "NATIVE_SCRIPT",
    "ROMANIZED",
    "CODE_MIXED",
    "INFORMAL",
]

SCRIPTS = [
    "Latin",
    "Devanagari",
    "Malayalam",
    "Tamil",
    "Telugu",
    "Kannada",
    "Other",
]

SOURCE_TYPES = ["REAL", "SYNTHETIC", "AUGMENTED"]
