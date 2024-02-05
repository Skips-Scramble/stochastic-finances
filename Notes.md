### General
- Months represent status at the beginning of the month
- Have a thing that calculates total salary for each month (so like money invested + spent + saved) and use as a check
- How to deal with health care
- It would be good to have it calculate back from 110 (or whatever) and show you how much you would need at each age of retirement
  - This would be part of a suite of results/outputs from the calculations
  - Helpful to know how much more you'd need at 55 versus 60 versus 65, etc.
  - Maybe build in a recommended retirement age
    - Define this by the age at which you will go from having negative retirement at age 110 to positive
- Add logging

## Rates
- Are interest rates (risk-free and S&P) normally distributed? or Uniform? or What?
  - Maybe normal with an unusual standard deviation?
  - Make chart showing this and explain to user
  - Should I use S&P interest rates in actuality? Or just say, "They're normal, so we're using normal"?
    - Maybe create a checkbox to use historic S&P 500 and apply it to your current situation?
- Does your market interest change post-retirement?
- I think I need to reevaluate the randomness here. E.g. it's not very likely that you will double your savings. But more likely you will go down to 0. So skew it lower more than higher.

##Inputs
- (.json)
  - Use pydantic to validate
  - Year over year changes to retirement and savings should be the same type (percent versus total dollars)
    - Maybe eventually have this be an option for both?
  - Is this even applicable anymore?
    - What if I set up an API?
- Website
  - Need to do some validation/formatting
    - Pass in everything as string and validate from there?
	- Format things to look nice
	  - Probably should create some standar formatting utils somewhere and make sure those are invoked everywhere
  - Better names for the input fields
  - Instead of having things in age in years and age in months, should do everything date based? Option for both? Provide calculator?
  - Make payments be able to be added dynamically, multiple times
  - Have modals pop up on mouse-over with explanations
  - Should have an "advanced options" toggle which would display more things
    - Should have the ability to switch back to advanced defaults in case you are screwing around and forgot where you are and want to reset or something like that

## Savings
- Adjust amount saved per month
  - Do this via annual pay raises (actually, should ultimately make this user-generated frequency)
    - This also adjusts for inflation assuming your pay is inflation-adjusted
  - Can do a flat savings increase or a percentage
- Add bonuses eventually

## Social Security
- SS withdraw amount could be assumed, or calculated
  - Should also have an override for if SS is assumed at all upon retirement
- Can you withdraw SS beginning at any age/month combo?
- Are you working?
- Are you still contributing to retirement?
- Are you withdrawing SS?

## Payments
- Add in optional TVM calc for payments per month
- Right now the person has to enter in their information one at a time (like for cars). Should there be a thing to just says, 
  "buy new car every X years, and just adjust according to inflation?"
- Need to add an employer contribution bit
  - I suppose this could be baked into the monthly, but if you're like me with annual contributions, then you'd need something extra
  - Analogous to non-base payments, but like non-base retirement
- I think this could maybe account for negative payments (i.e. savings) as well?
  - If you expect to have a reverse mortgage, or an annuity or something like that, this would be able to be input here as negative amounts?
  - Maybe should be its own thing?
- Since this is getting stored as a dictionary, can't have duplicate names. Need to fix.
- Make a dropdown for selecting frequency (one time, Monthly, quarterly, biannually, yearly)
  
## Retirement
- Change it so that retirement increase only changes at the start of a calendar year
- Reverse mortgage?
- This kind of assumes a Roth style account where taxes aren't a thing. Probably should add logic to deal with that
- Maybe use the costs calculated and TVM that back to figure out the present value of all of that to give a retirement value
- Make it so that retirement can't go negative is savings is positive
- Eventually need to figure out how to pull money from savings versus retirement in a reasonable way
- Need to factor in taxes on retirement (if applicable) to know your true value of things

## Outputs
- Need to format dollars using some sort of function
  - Negatives, percentages
- Save outputs so you don't have to recalculate
- Maybe create a dashboard so you can see all of the submissions and their outputs
  - Add a "save results" option for this that prompts you with a name and will then also save the inputs that went into it
  
#Front End
- Make it easier to update forms without redirecting to a new webpage
  - Formsets? Inline formsets?
- Create general readme to explain what things mean and how it works
  - Make sure all inputs are in todays dollars
- Get hoover over modals to explain what things mean
- How to have something that says, "loading" or something like that when you go to calculate