import datetime

class BaseScenario:
    def __init__(
            self,
            assumptions: dict,
    )
        
    @cached_property
    def birthdate(self) -> datetime.date:
        return datetime.strptime(self.assumptions["birthday"], "%m/%d/%Y").date()
    
    def calc_date_on_age(
        birthdate: datetime.date, age_yrs: int, age_mos: int
    ) -> datetime.date:
        """Calculates a date based on a birthdate and a given age in years and months"""
        if birthdate.month + age_mos <= 12:
            month = birthdate.month + age_mos
            spill_over = 0
        else:
            month = birthdate.month + age_mos - 12
            spill_over = 1

        year = birthdate.year + age_yrs + spill_over
        return date(year, month, 1)
    
    @cached_property
    def deathdate(self) -> datetime.date:
        return calc_date_on_age(birthdate, death_years, 0)
    