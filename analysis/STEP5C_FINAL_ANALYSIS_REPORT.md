# STEP 5C — FINAL MODEL COMPARISON AND ERROR ANALYSIS

## Objective

Compare the existing classical NLP models and XLM-RoBERTa using their recorded evaluation results, and perform a compact error analysis of the best classical model.

## Model Comparison

| Rank | Model | Accuracy | Weighted F1 | Macro F1 |
|---:|---|---:|---:|---:|
| 1 | Linear SVM | 0.8926 | 0.8927 | 0.8927 |
| 2 | Logistic Regression | 0.8425 | 0.8404 | 0.8403 |
| 3 | Multinomial Naive Bayes | 0.8366 | 0.8326 | 0.8325 |
| 4 | XLM-RoBERTa | 0.8292 | 0.8050 | 0.8048 |

**Best overall model based on Macro F1: Linear SVM (0.8927)**

## Error Analysis

Error analysis was performed using **Linear SVM**.

Total test errors: **330** out of **3073**.

Error rate: **0.1074**.

### Representative Misclassifications

**Example 1**
- Text: `How do I locate my card?`
- True intent: `card_arrival`
- Predicted intent: `get_physical_card`

**Example 2**
- Text: `I ordered a card but it has not arrived. Help please!`
- True intent: `card_arrival`
- Predicted intent: `transfer_not_received_by_recipient`

**Example 3**
- Text: `When will I get my card?`
- True intent: `card_arrival`
- Predicted intent: `card_delivery_estimate`

**Example 4**
- Text: `How long does a card delivery take?`
- True intent: `card_arrival`
- Predicted intent: `card_delivery_estimate`

**Example 5**
- Text: `How do I know when my card will arrive?`
- True intent: `card_arrival`
- Predicted intent: `card_delivery_estimate`

**Example 6**
- Text: `I'm starting to think my card is lost because it still hasn't arrived, can you help?`
- True intent: `card_arrival`
- Predicted intent: `lost_or_stolen_card`

**Example 7**
- Text: `Can I link another card to my account?`
- True intent: `card_linking`
- Predicted intent: `getting_spare_card`

**Example 8**
- Text: `Is it a good time to exchange?`
- True intent: `exchange_rate`
- Predicted intent: `exchange_via_app`

**Example 9**
- Text: `The exchange rate would be?`
- True intent: `exchange_rate`
- Predicted intent: `wrong_exchange_rate_for_cash_withdrawal`

**Example 10**
- Text: `The exchange rate was wrong when I bought something outside the country.`
- True intent: `card_payment_wrong_exchange_rate`
- Predicted intent: `wrong_exchange_rate_for_cash_withdrawal`

**Example 11**
- Text: `Why am I being charged more ?`
- True intent: `card_payment_wrong_exchange_rate`
- Predicted intent: `card_payment_fee_charged`

**Example 12**
- Text: `The exchange rate seems off on this transaction`
- True intent: `card_payment_wrong_exchange_rate`
- Predicted intent: `wrong_exchange_rate_for_cash_withdrawal`

**Example 13**
- Text: `How can I check the exchange rate applied to my transaction?`
- True intent: `card_payment_wrong_exchange_rate`
- Predicted intent: `wrong_exchange_rate_for_cash_withdrawal`

**Example 14**
- Text: `There is a fee I don't recognize on my statement.`
- True intent: `extra_charge_on_statement`
- Predicted intent: `card_payment_not_recognised`

**Example 15**
- Text: `Can you explain what this random $1 charge is?`
- True intent: `extra_charge_on_statement`
- Predicted intent: `direct_debit_payment_not_recognised`

**Example 16**
- Text: `When will the $1 transaction be credited to me?`
- True intent: `extra_charge_on_statement`
- Predicted intent: `transfer_not_received_by_recipient`

**Example 17**
- Text: `Where did this fee come from?`
- True intent: `extra_charge_on_statement`
- Predicted intent: `transfer_fee_charged`

**Example 18**
- Text: `It's been two weeks, why has the transaction for $1.00 not been reversed?`
- True intent: `extra_charge_on_statement`
- Predicted intent: `reverted_card_payment?`

**Example 19**
- Text: `What is the €1 fee for?`
- True intent: `extra_charge_on_statement`
- Predicted intent: `top_up_by_bank_transfer_charge`

**Example 20**
- Text: `I made a withdrawal from my account but it has not posted?`
- True intent: `pending_cash_withdrawal`
- Predicted intent: `cash_withdrawal_not_recognised`

### Most Frequent Confusion Pairs

| True Intent | Predicted Intent | Count |
|---|---|---:|
| why_verify_identity | verify_my_identity | 5 |
| unable_to_verify_identity | verify_my_identity | 5 |
| pending_transfer | balance_not_updated_after_bank_transfer | 5 |
| virtual_card_not_working | getting_virtual_card | 5 |
| fiat_currency_support | exchange_via_app | 4 |
| wrong_exchange_rate_for_cash_withdrawal | card_payment_wrong_exchange_rate | 4 |
| balance_not_updated_after_bank_transfer | transfer_not_received_by_recipient | 4 |
| card_arrival | card_delivery_estimate | 3 |
| card_payment_wrong_exchange_rate | wrong_exchange_rate_for_cash_withdrawal | 3 |
| pin_blocked | card_not_working | 3 |

## Multilingual Evaluation

The available multilingual dataset contained 41 rows.
0 rows had directly compatible BANKING77 labels.
41 rows had incompatible intent labels.

Because the intent taxonomies were incompatible, quantitative accuracy and F1 evaluation was not performed on the multilingual dataset. No artificial label mapping was introduced.

## Interpretation

The comparison demonstrates the performance of traditional TF-IDF-based classifiers alongside a multilingual Transformer model.
Macro F1 was used as the primary model-selection criterion because BANKING77 contains 77 intent classes and Macro F1 gives equal importance to each class.
The error analysis identifies representative intent confusions made by the best classical classifier.

## Reproducibility

- Existing trained models were reused.
- No new model was trained in Step 5C.
- Raw datasets were not modified.
- Processed datasets were not modified.
- No artificial multilingual label mapping was used.