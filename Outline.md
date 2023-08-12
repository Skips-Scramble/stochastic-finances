## Outline
- Build in Retirement calcs
  - Reformat everything so that:
	- base (unvaried) retirement stuff is before the variable savings stuff (maybe not?)


Implementation
- I think I want to have modules that can be mixed at matched
- You create base data (things that we aren't going to vary)
  - Age Yrs
  - Age Months
  - Month
  - Count
  - Savings
  - Retirement Age Yrs
  - Retirement Age Mos
  - SS Withdraw Age Yrs
  - SS Withdraw Age Mos
  - Base Spend per Month
  - Rent per Month
  - Base SS Withdraw
- Things that will vary
  - Interest rate
  - Inflation
  - Savings per month added
    - Amount should have some trend factor applied
  - Extra per month in retirement
  - SS amount
  - Spend per month
  - Actual SS withdraw
- Not sure
  - Retirement saved per month
  - Salary
    - Base a few things off of this
	  - Retirement per month/year
	  - Savings per month/year
  - Rent/housing/down payment
  - Car payment/down payment
  - Misc
  - Health care costs
  - 
  