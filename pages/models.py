from django.db import models

from accounts.models import CustomUser

from .model_validators import (
    decimal_validator,
    validate_base_monthly_bills,
    validate_base_per_yr_increase,
    validate_base_retirement,
    validate_base_retirement_per_mo,
    validate_base_retirement_per_yr_increase,
    validate_base_saved_per_mo,
    validate_base_savings,
    validate_down_pmt,
    validate_monthly_pmt,
    validate_pmt_length_yrs,
    validate_pmt_start_age_yrs,
    validate_range_age_mos,
    validate_range_age_yrs,
    validate_range_birthdate,
    validate_rates_per_yr,
    validate_retirement_extra_expenses,
    validate_savings_lower_limit,
)


class GeneralInputsModel(models.Model):
    """General inputs to the model"""

    is_active = models.BooleanField(
        default=False,
    )

    birthdate = models.DateField(
        validators=[validate_range_birthdate],
    )
    retirement_age_yrs = models.IntegerField(
        validators=[validate_range_age_yrs],
    )
    retirement_age_mos = models.IntegerField(
        validators=[validate_range_age_mos],
    )

    created_by = models.ForeignKey(
        CustomUser,
        related_name="general_inputs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "General_Inputs"
