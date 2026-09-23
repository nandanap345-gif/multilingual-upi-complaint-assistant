# STEP 4B — Linear SVM Baseline

## 1. Objective

Step 4B establishes a classical Linear Support Vector Machine baseline for BANKING77 intent classification using TF-IDF text representation.

## 2. Dataset

- Dataset: BANKING77
- Training records: 10003
- Testing records: 3073
- Intent classes: 77
- Original train/test separation preserved.

## 3. TF-IDF Representation

- Lowercasing: disabled
- Accent stripping: disabled
- N-gram range: (1, 2)
- Sublinear TF: enabled
- Minimum document frequency: 1
- Maximum document frequency: 1.0
- Vocabulary size: 25523
- Training TF-IDF shape: (10003, 25523)
- Testing TF-IDF shape: (3073, 25523)

## 4. Linear SVM Configuration

- Model: LinearSVC
- C: 1.0
- max_iter: 5000
- random_state: 42

## 5. Evaluation Results

| Metric | Score |
|---|---:|
| Accuracy | 0.8926 |
| Weighted Precision | 0.8966 |
| Weighted Recall | 0.8926 |
| Weighted F1 | 0.8927 |
| Macro Precision | 0.8966 |
| Macro Recall | 0.8926 |
| Macro F1 | 0.8927 |

## 6. Leakage Prevention

The TF-IDF vectorizer was fitted exclusively on the training data. The test data was transformed using the fitted training vectorizer. No test data was used during training or vocabulary construction.

## 7. Comparison with Step 4A

Step 4A used TF-IDF with One-vs-Rest Logistic Regression. Step 4B uses TF-IDF with Linear SVM. Both models use the same processed BANKING77 train/test data so that their performance can be compared fairly.

## 8. Model Artifacts

- Model: `C:\Users\nanda\Downloads\Multilingual_UPI_Complaint_Assistant\models\step4b_linear_svm.joblib`
- Vectorizer: `C:\Users\nanda\Downloads\Multilingual_UPI_Complaint_Assistant\models\step4b_tfidf_vectorizer.joblib`
- Results: `C:\Users\nanda\Downloads\Multilingual_UPI_Complaint_Assistant\analysis\step4b_results.json`
- Confusion matrix: `C:\Users\nanda\Downloads\Multilingual_UPI_Complaint_Assistant\analysis\step4b_confusion_matrix.npy`

## 9. Classification Report

```text
                                                  precision    recall  f1-score   support

                           Refund_not_showing_up       0.93      0.95      0.94        40
                                activate_my_card       0.97      0.95      0.96        40
                                       age_limit       1.00      1.00      1.00        40
                         apple_pay_or_google_pay       1.00      1.00      1.00        40
                                     atm_support       0.92      0.87      0.89        39
                                automatic_top_up       0.97      0.97      0.97        40
         balance_not_updated_after_bank_transfer       0.69      0.78      0.73        40
balance_not_updated_after_cheque_or_cash_deposit       0.88      0.93      0.90        40
                         beneficiary_not_allowed       0.95      0.93      0.94        40
                                 cancel_transfer       0.95      0.95      0.95        40
                            card_about_to_expire       0.97      0.97      0.97        40
                                 card_acceptance       0.89      0.82      0.85        38
                                    card_arrival       0.87      0.85      0.86        40
                          card_delivery_estimate       0.85      0.85      0.85        40
                                    card_linking       0.93      0.97      0.95        40
                                card_not_working       0.71      0.88      0.79        40
                        card_payment_fee_charged       0.97      0.90      0.94        40
                     card_payment_not_recognised       0.91      0.78      0.84        40
                card_payment_wrong_exchange_rate       0.86      0.90      0.88        40
                                  card_swallowed       1.00      0.90      0.95        40
                          cash_withdrawal_charge       0.95      0.93      0.94        40
                  cash_withdrawal_not_recognised       0.91      0.97      0.94        40
                                      change_pin       1.00      0.92      0.96        39
                                compromised_card       0.90      0.90      0.90        39
                         contactless_not_working       1.00      0.88      0.93        40
                                 country_support       0.90      0.95      0.93        39
                           declined_card_payment       0.79      0.93      0.85        40
                        declined_cash_withdrawal       0.86      0.93      0.89        40
                               declined_transfer       0.94      0.82      0.88        40
             direct_debit_payment_not_recognised       0.90      0.88      0.89        40
                          disposable_card_limits       0.92      0.85      0.88        40
                           edit_personal_details       0.98      1.00      0.99        40
                                 exchange_charge       0.89      0.85      0.87        40
                                   exchange_rate       0.88      0.95      0.92        40
                                exchange_via_app       0.82      0.90      0.86        40
                       extra_charge_on_statement       0.77      0.85      0.81        40
                                 failed_transfer       0.73      0.82      0.78        40
                           fiat_currency_support       0.97      0.78      0.86        40
                     get_disposable_virtual_card       0.92      0.85      0.88        40
                               get_physical_card       0.87      0.97      0.92        40
                              getting_spare_card       0.93      0.93      0.93        40
                            getting_virtual_card       0.76      0.95      0.84        40
                             lost_or_stolen_card       0.86      0.90      0.88        40
                            lost_or_stolen_phone       1.00      0.97      0.99        40
                             order_physical_card       0.90      0.88      0.89        40
                              passcode_forgotten       0.98      1.00      0.99        40
                            pending_card_payment       0.86      0.90      0.88        40
                         pending_cash_withdrawal       0.97      0.88      0.92        40
                                  pending_top_up       0.89      0.82      0.86        40
                                pending_transfer       0.82      0.70      0.76        40
                                     pin_blocked       0.89      0.85      0.87        39
                                 receiving_money       0.97      0.97      0.97        40
                                  request_refund       0.92      0.88      0.90        40
                          reverted_card_payment?       0.88      0.95      0.92        40
                  supported_cards_and_currencies       0.81      0.97      0.89        40
                               terminate_account       0.95      1.00      0.98        40
                  top_up_by_bank_transfer_charge       0.89      0.82      0.86        40
                           top_up_by_card_charge       0.90      0.93      0.91        40
                        top_up_by_cash_or_cheque       0.89      0.85      0.87        40
                                   top_up_failed       0.79      0.78      0.78        40
                                   top_up_limits       0.87      0.97      0.92        40
                                 top_up_reverted       0.86      0.90      0.88        40
                              topping_up_by_card       0.86      0.78      0.82        40
                       transaction_charged_twice       0.93      1.00      0.96        40
                            transfer_fee_charged       0.89      0.85      0.87        40
                           transfer_into_account       0.88      0.90      0.89        40
              transfer_not_received_by_recipient       0.76      0.80      0.78        40
                                 transfer_timing       0.86      0.80      0.83        40
                       unable_to_verify_identity       0.91      0.80      0.85        40
                              verify_my_identity       0.73      0.82      0.78        40
                          verify_source_of_funds       0.93      0.95      0.94        40
                                   verify_top_up       0.95      1.00      0.98        40
                        virtual_card_not_working       1.00      0.72      0.84        40
                              visa_or_mastercard       1.00      0.93      0.96        40
                             why_verify_identity       0.83      0.85      0.84        40
                   wrong_amount_of_cash_received       0.95      0.90      0.92        40
         wrong_exchange_rate_for_cash_withdrawal       0.82      0.78      0.79        40

                                        accuracy                           0.89      3073
                                       macro avg       0.90      0.89      0.89      3073
                                    weighted avg       0.90      0.89      0.89      3073

```

## 10. Conclusion

Step 4B establishes the Linear SVM baseline for BANKING77 intent classification. Its performance can be compared with the Step 4A Logistic Regression baseline before proceeding to subsequent modeling stages.