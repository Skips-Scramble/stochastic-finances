# pages/claude.md

## General Tab: Medical/Healthcare Toggles

This document explains the three General tab healthcare options and their interactions.

### Option 1: "Please automatically include healthcare costs for me" (`add_healthcare`)
- Master healthcare toggle.
- When enabled, model-driven healthcare costs are included.
- Medicare premiums (Part B and Part D) are also included for age 65+.
- When disabled, healthcare-related automatic streams are zeroed out.

### Option 2: "Include ACA insurance cost when retired and under 65" (`include_pre_medicare_insurance`)
- Adds a pre-Medicare private insurance (ACA) cost stream.
- Applies only if all are true:
  - `add_healthcare` is enabled,
  - this toggle is enabled,
  - retirement age is under 65.
- Applies from retirement date until Medicare eligibility (65).
- Uses a hardcoded base monthly premium and inflates over time.

### Option 3: "Include your own monthly medical bills estimate" (`add_medical_bills` + `monthly_medical_bills`)
- User-entered monthly out-of-pocket estimate (copays, prescriptions, dental, etc.).
- Independent from Option 1 in meaning.
- Inflates over time.
- If disabled, this stream is zero.

## Key Difference Between Option 1 and Option 3
- Option 1 is automatic/model-driven healthcare cost inclusion.
- Option 3 is your own custom monthly medical bills estimate.
- Option 1 does not act as a default value for Option 3.
- Option 3 does not replace Option 1.

### Hover/Tooltip Clarification
- Option 1 hover text should clearly say it includes automatic model-driven costs (including Medicare at 65+).
- Option 3 hover text should clearly say it is your own custom amount.
- Tooltips should make clear these options are additive and can be enabled together.

## Can You Use Option 1 and Option 3 Together?
Yes.
- If both are enabled, both cost streams are included in monthly expenses.
- This means total medical-related expenses are higher than using either one alone.

## Practical Guidance
- Use Option 1 if you want built-in healthcare and Medicare assumptions.
- Use Option 3 if you want to model additional personal out-of-pocket costs.
- Enable both when you want baseline healthcare costs plus your own extra medical estimate.
- Enable Option 2 only when retiring before 65 and you want ACA-style bridge coverage modeled.
