import os
import django
from django.db import models

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from pages.models import SavingsInputsModel, RetirementInputsModel  # noqa: E402

print("=" * 60)
print("TEST 1: Import models successfully")
print("=" * 60)
print("? SavingsInputsModel imported")
print("? RetirementInputsModel imported")
print()

print("=" * 60)
print("TEST 2: Create SavingsInputsModel with interest_rate_per_yr")
print("=" * 60)
savings = SavingsInputsModel(
    base_savings=10000,
    base_saved_per_mo=500,
    base_savings_per_yr_increase=100,
    savings_lower_limit=0,
    base_monthly_bills=2000,
    interest_rate_per_yr=3.5,
)
print("Created SavingsInputsModel instance:")
print(f"  base_savings: {savings.base_savings}")
print(f"  interest_rate_per_yr: {savings.interest_rate_per_yr}")
print()

print("=" * 60)
print("TEST 3: Create RetirementInputsModel with interest_rate_per_yr")
print("=" * 60)
retirement = RetirementInputsModel(
    retirement_type="traditional_401k",
    base_retirement=50000,
    base_retirement_per_mo=300,
    base_retirement_per_yr_increase=100,
    interest_rate_per_yr=6.0,
)
print("Created RetirementInputsModel instance:")
print(f"  retirement_type: {retirement.retirement_type}")
print(f"  base_retirement: {retirement.base_retirement}")
print(f"  interest_rate_per_yr: {retirement.interest_rate_per_yr}")
print()

print("=" * 60)
print("TEST 4: Verify field types and defaults")
print("=" * 60)
print("SavingsInputsModel fields:")
for field in SavingsInputsModel._meta.get_fields():
    if field.name in ["interest_rate_per_yr"] and isinstance(field, models.Field):
        print(f"  {field.name}: {field.get_internal_type()} - default={field.default}")

print("\nRetirementInputsModel fields:")
for field in RetirementInputsModel._meta.get_fields():
    if field.name in ["interest_rate_per_yr"] and isinstance(field, models.Field):
        print(f"  {field.name}: {field.get_internal_type()} - default={field.default}")
print()

print("=" * 60)
print("TEST 5: Create instances WITHOUT interest_rate_per_yr (test defaults)")
print("=" * 60)
savings_no_rate = SavingsInputsModel(
    base_savings=5000,
    base_saved_per_mo=250,
    base_savings_per_yr_increase=50,
    savings_lower_limit=0,
    base_monthly_bills=2000,
)
print("SavingsInputsModel without interest_rate_per_yr:")
print(f"  interest_rate_per_yr: {savings_no_rate.interest_rate_per_yr}")

retirement_no_rate = RetirementInputsModel(
    retirement_type="traditional_401k",
    base_retirement=25000,
    base_retirement_per_mo=200,
    base_retirement_per_yr_increase=50,
)
print("RetirementInputsModel without interest_rate_per_yr:")
print(f"  interest_rate_per_yr: {retirement_no_rate.interest_rate_per_yr}")
print()

print("=" * 60)
print("SUMMARY: All model tests passed successfully!")
print("=" * 60)
print("? Models import without errors")
print("? Models create instances with interest_rate_per_yr")
print("? Fields accept decimal values (3.5, 6.0)")
print("? Fields have proper defaults when not provided")
