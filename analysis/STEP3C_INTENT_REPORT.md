# Step 3C Intent Analysis Report — Revised (Strict UPI criterion)

Generated on: 2026-08-15T07:54:17.790074Z

Summary

- Total intents: 77
- DIRECT: 11 intents — train=1665 test=440 combined=2105
- BORDERLINE: 21 intents — train=2696 test=840 combined=3536
- IRRELEVANT: 45 intents — train=5642 test=1800 combined=7442

Methodology

This revision applies a strict UPI relevance criterion: classify as DIRECT only when the intent's meaning transfers to a UPI transaction context without changing its fundamental meaning. BORDERLINE indicates genuine ambiguity (mechanism, KYC, or top-up rails). IRRELEVANT indicates clear card/ATM/cash/cheque or unrelated account-management domains.

Final DIRECT intents (11)

1. cancel_transfer — 157/40/197 — DIRECT
   - reason: Transfer cancellation maps directly to UPI transfer semantics.
   - examples: Cancel a transaction; Am I able to cancel a transfer I just made
2. declined_transfer — 133/40/173 — DIRECT
   - reason: Transfer declined is a direct transfer failure.
   - examples: Transfer unable to be completed, states 'declined'; Why was my transfer request decline?
3. failed_transfer — 137/40/177 — DIRECT
   - reason: Transfer failure maps directly to UPI transfer-failure semantics.
   - examples: What is happening? I have tried to transfer money 5x already.; Is there a reason that my transfer failed?
4. pending_transfer — 148/40/188 — DIRECT
   - reason: Transfer pending is directly applicable to UPI semantics.
   - examples: i put in money for vacation and its not showing...; I can't figure out why a transfer is still pending?
5. transfer_not_received_by_recipient — 171/40/211 — DIRECT
   - reason: Recipient not receiving transfer maps to UPI complaints.
   - examples: I am worried that too much time has gone by for a transfer to be completed.; My money transaction can't be seen by the person I sent it to
6. transfer_into_account — 113/40/153 — DIRECT
   - reason: Transfer initiation semantics align with UPI transfers.
   - examples: I want to transfer money. How do I do that for my account?; How do I transfer money into my account?
7. transfer_timing — 128/40/168 — DIRECT
   - reason: Transfer timing/delay questions directly apply to UPI transfers.
   - examples: How long am I to wait before the transfer gets to my account?; Will the transfer show up in my account soon?
8. transfer_fee_charged — 172/40/212 — DIRECT
   - reason: Unexpected fee on transfer is directly transferable to UPI transfer fees.
   - examples: I was transferring some money to a friend...; There is a fee for a transfer, please explain that to me.
9. transaction_charged_twice — 175/40/215 — DIRECT
   - reason: Duplicate charge is a payment dispute applicable to UPI.
   - examples: A transaction shows duplicate times.; There is a repeat charge for the same item
10. request_refund — 169/40/209 — DIRECT
   - reason: Refund requests map to payment/refund semantics (UPI refunds possible).
   - examples: How long does it take to get a refund on something I bought?; Please tell me how to get a refund for something I bought.
11. Refund_not_showing_up — 162/40/202 — DIRECT
   - reason: Refund not credited is a payment/refund complaint relevant to UPI.
   - examples: I don't see my refund money yet in my account...; Why am I missing my refund

Final BORDERLINE intents (21)

(Items listed with counts and two representative examples; included only when research scope allows generic banking/payment proxies)

1. automatic_top_up — 127/40/167 — BORDERLINE
   - examples: Can I add money automatically to my account while traveling?; i need help finding the auto top up option.
2. balance_not_updated_after_cheque_or_cash_deposit — 181/40/221 — BORDERLINE
   - examples: Why is my last cheque deposit taking so long?; I am still waiting for a the cash I deposited this morning
3. change_pin — 122/40/162 — BORDERLINE
   - examples: Is it possible for me to change my PIN number?; What are the steps to change my PIN to something else?
4. direct_debit_payment_not_recognised — 182/40/222 — BORDERLINE
   - examples: Hi, i found a large amount payment in my old statements...; Please help my find out why there is an odd direct debit in my records.
5. exchange_charge — 121/40/161 — BORDERLINE
   - examples: How much is the exchange fee?; Are there any hidden extra fees for currency exchanges?
6. exchange_rate — 112/40/152 — BORDERLINE
   - examples: What is my money worth in other countries?; Will my money be of equal value when I travel abroad?
7. exchange_via_app — 118/40/158 — BORDERLINE
   - examples: Can I change from AUD to GBP?; I need to exchange between different currencies, like GBP and USD. Can I do that with your app?
8. passcode_forgotten — 105/40/145 — BORDERLINE
   - examples: Help me! I don't know what my password is.; I thought I knew my password but I guess I was wrong, what can I do now?
9. pending_top_up — 149/40/189 — BORDERLINE
   - examples: How long does a top-up take to go through?; I am under the impression that my top up is still pending
10. pin_blocked — 115/40/155 — BORDERLINE
    - examples: I have exceeded the number of PIN attempts; I mistook my pin and now I am locked. Can you unlock me?
11. receiving_money — 95/40/135 — BORDERLINE
    - examples: Can my salary be received here?; How can my boss pay me directly to the card?
12. reverted_card_payment? — 161/40/201 — BORDERLINE
    - examples: I wanted to purchase something online but the payment was returned back to me.; I tried to use my debit card, but the payment did not work.
13. top_up_by_bank_transfer_charge — 111/40/151 — BORDERLINE
    - examples: Is there a top up fee for transfer?; Will there be a charge for topping up by account with a SEPA transfer?
14. top_up_failed — 145/40/185 — BORDERLINE
    - examples: I think my top-up has failed.; Top-up is not working
15. top_up_reverted — 146/40/186 — BORDERLINE
    - examples: My top up did not show up as shown and my money has disappeared...; Has my top-up been cancelled?
16. topping_up_by_card — 103/40/143 — BORDERLINE
    - examples: My money I had was gone and I could not get gas!; i can not see my top up
17. unable_to_verify_identity — 102/40/142 — BORDERLINE
    - examples: Can you help me with proving my identity?; What proof do you need for my identification?
18. verify_my_identity — 104/40/144 — BORDERLINE
    - examples: What do you require for identity verification?; How can I prove I am me?
19. verify_source_of_funds — 113/40/153 — BORDERLINE
    - examples: where exactly does money come from; Where did my money come from?
20. why_verify_identity — 121/40/161 — BORDERLINE
    - examples: Why do you have an identity check?; I do not feel comfortable verifying my identity.
21. wrong_exchange_rate_for_cash_withdrawal — 163/40/203 — BORDERLINE
    - examples: The wrong exchange rate was applied to me while pulling out cash.; I got less cash because of the exchange rate.

Final IRRELEVANT intents (45)

... (see `analysis/step3c_revised_strict.json` for full assignments and per-intent details)

Changed classifications (from prior manual pass)

- automatic_top_up: DIRECT -> BORDERLINE — auto-topup mechanism ambiguous; not strictly UPI.
- balance_not_updated_after_bank_transfer: DIRECT -> IRRELEVANT — examples reference bank-transfer rail, not UPI.
- balance_not_updated_after_cheque_or_cash_deposit: DIRECT -> BORDERLINE — cheque/cash mechanism; borderline.
- beneficiary_not_allowed: BORDERLINE -> IRRELEVANT — dataset context indicates bank-specific policy.
- declined_cash_withdrawal: BORDERLINE -> IRRELEVANT — ATM/cash-specific.
- pending_cash_withdrawal: BORDERLINE -> IRRELEVANT — ATM/cash-specific.
- pending_top_up: DIRECT -> BORDERLINE — top-up mechanism ambiguous.
- receiving_money: DIRECT -> BORDERLINE — examples reference salary/card; ambiguous for UPI.
- reverted_card_payment?: DIRECT -> BORDERLINE — examples are card-specific.
- top_up_by_bank_transfer_charge: DIRECT -> BORDERLINE — bank-transfer top-up is a transfer-rail proxy; ambiguous.
- top_up_by_card_charge: DIRECT -> IRRELEVANT — card-topup fee; card-specific.
- top_up_by_cash_or_cheque: DIRECT -> IRRELEVANT — cash/cheque mechanism.
- top_up_failed: DIRECT -> BORDERLINE — ambiguous mechanism in examples.
- top_up_limits: DIRECT -> IRRELEVANT — product limits, not UPI-specific.
- top_up_reverted: DIRECT -> BORDERLINE — top-up revert tied to mechanism.
- verify_top_up: DIRECT -> IRRELEVANT — examples reference card top-up verification.

Methodological limitations

- BANKING77 is heavily card/ATM/cash-focused; UPI-specific lexical cues are largely absent. Mapping intents to UPI is a methodological adaptation — it does not make the original data UPI-specific. Any model trained on these proxies must be validated on real UPI complaints.
- Several intents are ambiguous in mechanism (top-ups, PIN, passcodes). These were classified BORDERLINE; inclusion requires explicit scope decisions.
- Class imbalance: strict UPI-relevant intents are a minority; expect the need for additional UPI-native data or reweighting.

UPI scope recommendation (strict)

- Strongly defensible (include for UPI complaint classifier): cancel_transfer, declined_transfer, failed_transfer, pending_transfer, transfer_not_received_by_recipient, transfer_into_account, transfer_timing, transfer_fee_charged, transaction_charged_twice, request_refund, Refund_not_showing_up.
- Borderline (include only if accepting generic banking/payment proxies or KYC/auth proxies): automatic_top_up, balance_not_updated_after_cheque_or_cash_deposit, change_pin, direct_debit_payment_not_recognised, exchange_charge, exchange_rate, exchange_via_app, passcode_forgotten, pending_top_up, pin_blocked, receiving_money, reverted_card_payment?, top_up_by_bank_transfer_charge, top_up_failed, top_up_reverted, topping_up_by_card, unable_to_verify_identity, verify_my_identity, verify_source_of_funds, why_verify_identity, wrong_exchange_rate_for_cash_withdrawal.
- Exclude (IRRELEVANT): card lifecycle, card payments, ATM/cash, currency/FX, and other non-UPI intents listed in `analysis/step3c_revised_strict.json`.

Notes

- The revised assignments are saved as `analysis/step3c_revised_strict.json`. No raw data was modified. Do not proceed to Step 3D without user instruction.
