### Assumptions

#### Inputs
1. Exactly one scenario must be selected, except for payments and retirement

#### Payments
1. We are assuming all money is in today's dollars
1. We are assuming that if a payment was started in the past, that the down payment and regular payments are in the dollars of the time. I.e. not adjusted for today's dollars
1. We are assuming that if a payment was started in the past, that these payments are incorporated into the monthly savings calcs and no changes will be made until after the last payment, when your savings monthly amount will be raised by the payment amounts

#### Calculations
1. We are assuming that in this month (month 0), everything is already trued up. So what you have in all of your accounts will remain until the end of the month. Then the start of next month, all adjustments for payments, interest, ect. will be made. 
  1. That is, contributions first, then interest

1. We are assuming that you need to be within these ages

#### Savings Threshold & Account Transfers
When the savings account balance drops below the `savings_lower_limit` (inflation-adjusted each month), the system automatically withdraws from other accounts in a strict priority order to bring savings back up to the threshold. Each step only triggers if savings is still below the threshold after the previous step.

**Timing:**
- **Pre-retirement:** Only triggers after 10 years (120 months) have passed
- **Post-retirement:** Triggers immediately

**Transfer Priority Order:**
1. **Roth IRA (contributions only)** — No age restriction. Withdraws only contributions, not earnings.
2. **Brokerage Account** — No age restriction.
3. **Roth IRA (full balance)** — Requires age >= 59.5. Withdraws both contributions and earnings.
4. **Roth 401(k)** — Requires age >= 59.5.
5. **Traditional 401(k)** — Requires age >= 59.5. A 20% tax is deducted; only the net amount goes to savings.
6. **HSA** — Requires age >= 65 (for non-medical use).

At each step, the withdrawal amount is the lesser of the shortfall (threshold minus current savings) and the available balance in that account.