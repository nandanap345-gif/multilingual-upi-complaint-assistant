from src.upi_engine import analyse_complaint, build_complaint_summary, build_structured_summary, get_follow_up_questions, sanitize_text


def test_debit_and_failure_is_more_specific_than_general_failure():
    result = analyse_complaint("My UPI payment failed but money was deducted")
    assert result.primary_intent == "MONEY_DEDUCTED_PAYMENT_FAILED"
    assert result.confidence_label in {"Medium", "High"}


def test_fraud_has_high_urgency():
    result = analyse_complaint("I did not make this UPI transfer. This is fraud.")
    assert result.primary_intent == "FRAUD_OR_UNAUTHORIZED_TRANSACTION"
    assert result.severity == "High"


def test_long_numbers_and_upi_ids_do_not_enter_summary():
    result = analyse_complaint("My UPI ID is person@bank and reference is 123456789012")
    summary = build_complaint_summary(result)
    assert "person@bank" not in summary
    assert "123456789012" not in summary
    assert "UPI ID hidden" in summary


def test_malayalam_script_detection():
    result = analyse_complaint("പണം ഡെബിറ്റ് ആയി പക്ഷേ പേയ്മെന്റ് പരാജയപ്പെട്ടു")
    assert result.language == "Malayalam"
    assert result.writing_style == "NATIVE_SCRIPT"


def test_malayalam_transferred_but_not_received_routes_correctly():
    result = analyse_complaint("പണം ട്രാൻസ്ഫർ ചെയ്തു പക്ഷേ അത് അവിടെ എത്തിയില്ല")
    assert result.primary_intent == "MONEY_DEDUCTED_NO_RECIPIENT"
    assert result.confidence_label in {"Medium", "High"}


def test_unclear_text_requests_clarification():
    result = analyse_complaint("please help me")
    assert result.confidence_label == "Low"
    assert result.clarification


def test_sanitize_marks_six_digit_values():
    sanitized, flags = sanitize_text("My OTP is 123456")
    assert "123456" not in sanitized
    assert flags


def test_failed_and_debited_route_has_relevant_follow_up_questions():
    questions = get_follow_up_questions("MONEY_DEDUCTED_PAYMENT_FAILED")
    assert [question[0] for question in questions] == ["status", "reversed"]


def test_structured_summary_includes_safe_follow_up_answers():
    result = analyse_complaint("My UPI payment failed but money was deducted")
    summary = build_structured_summary(result, {"status": "Failed", "reversed": "No"})
    assert "Status: Failed" in summary
    assert "Reversed: No" in summary


def test_malayalam_failed_but_debited_routes_correctly():
    result = analyse_complaint("പണം ഡെബിറ്റ് ആയി പക്ഷേ പേയ്മെന്റ് പരാജയപ്പെട്ടു")
    assert result.primary_intent == "MONEY_DEDUCTED_PAYMENT_FAILED"
    assert result.confidence_label in {"Medium", "High"}


def test_malayalam_wrong_recipient_routes_correctly():
    result = analyse_complaint("തെറ്റായ യുപിഐ ഐഡിക്ക് പണം അയച്ചു")
    assert result.primary_intent == "WRONG_RECIPIENT"
    assert result.severity == "High"


def test_malayalam_refund_not_received_routes_correctly():
    result = analyse_complaint("റിഫണ്ട് വന്നില്ല")
    assert result.primary_intent == "REFUND_NOT_RECEIVED"
    assert result.confidence_label in {"Medium", "High"}


def test_malayalam_transfer_to_friend_not_received_routes_correctly():
    result = analyse_complaint("ഞാൻ എന്റെ ഫ്രണ്ടിന്റെ അക്കൗണ്ടിലേക്ക് പൈസ ട്രാൻസ്ഫർ ചെയ്തു പക്ഷേ അത് അവിടെ എത്തിയില്ല")
    assert result.primary_intent == "MONEY_DEDUCTED_NO_RECIPIENT"
    assert result.confidence_label in {"Medium", "High"}
