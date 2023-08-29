### General
- Months represent status at the beginning of the month
- Are interest rates (risk-free and S&P) normally distributed? or Uniform? or What?
  - Maybe normal with an unusual standard deviation?
  - Make chart showing this and explain to user
  - Should I use S&P interest rates in actuality? Or just say, "They're normal, so we're using normal"?
- Need to maybe allow non-variable fields upon request (i.e. don't vary interest, or don't vary savings added per month)
- Right now, there are yearly (base) interest and monthly (base) interest list being generated. But these are static variables,
so really don't need lists. Only really needed for outputting to csv
- Have a thing that calculates total salary for each month (so like money invested + spent + saved) and use as a check

## Savings
- Do I need to make a new variable for savings interest? Usually lower and less volatile - continuous flow
- Idea: Have interest rate change every quarter and choose a direction and magnitude between 0.05% and 0.15%?
  - Floor at 0.1%, cap at 5.5%?
  - This is essentially adjusted via uniform distribution. Should I change this? Look at historical data and see what's what?
    - Yeah, doesn't look like a ton of variance. But maybe that's OK?
- Adjust amount saved per month
  - Do this via annual pay raises (actually, should ultimately make this user-generated frequency)
    - This also adjusts for inflation assuming your pay is inflation-adjusted
  - Can do a flat savings increase or a percentage
- Add bonuses eventually

## Kids, College, Other
- Have options to put in other expenses, put in time periods, adjustments over time, starting/stopping

## Social Security
- SS withdraw amount could be assumed, or calculated
  - Should also have an override for if SS is assumed at all upon retirement
- Can you withdraw SS beginning at any age/month combo?

## Rent/Mortgage
- Need to make rent more dynamic (start, stop, multiple)

## Payments
- Need to make car payment more dynamic (start, stop, multiple occurrences)
- Make new cars have some chaos variable where it gets destroyed and you need a new one or something
- Add in optional TVM calc for payments per month
- Right now the person has to enter in their information one at a time (like for cars). Should there be a thing to just says, 
  "buy new car every X years, and just adjust according to inflation?"
  
## Retirement
- What money are you pulling from where?
- Reverse mortgage?
- This kind of assumes a Roth style account where taxes aren't a thing. Probably should add logic to deal with that