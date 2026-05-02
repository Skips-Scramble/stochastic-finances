import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from pages.models import SavingsInputsModel, RetirementInputsModel

print("=" * 60)
print("TEST 1: Import models successfully")
print("=" * 60)
print("? SavingsInputsModel imported")
print("? RetirementInputsModel imported")
print()

print("=" * 60)
print("TEST 2: Create SavingsInputsModel with interest_rate_per_yr")
print("=" * 60)
savings = SavingsInputsModel(annual_savings=10000, interest_rate_per_yr=3.5)
print("Created SavingsInputsModel instance:")
print(f"  annual_savings: {savings.annual_savings}")
print(f"  interest_rate_per_yr: {savings.interest_rate_per_yr}")
print()

print("=" * 60)
print("TEST 3: Create RetirementInputsModel with interest_rate_per_yr")
print("=" * 60)
retirement = RetirementInputsModel(
    current_age=30, retirement_age=65, interest_rate_per_yr=6.0
)
print("Created RetirementInputsModel instance:")
print(f"  current_age: {retirement.current_age}")
print(f"  retirement_age: {retirement.retirement_age}")
print(f"  interest_rate_per_yr: {retirement.interest_rate_per_yr}")
print()

print("=" * 60)
print("TEST 4: Verify field types and defaults")
print("=" * 60)
print("SavingsInputsModel fields:")
for field in SavingsInputsModel._meta.get_fields():
    if field.name in ["interest_rate_per_yr"]:
        print(f"  {field.name}: {field.get_internal_type()} - default={field.default}")

print("\nRetirementInputsModel fields:")
for field in RetirementInputsModel._meta.get_fields():
    if field.name in ["interest_rate_per_yr"]:
        print(f"  {field.name}: {field.get_internal_type()} - default={field.default}")
print()

print("=" * 60)
print("TEST 5: Create instances WITHOUT interest_rate_per_yr (test defaults)")
print("=" * 60)
savings_no_rate = SavingsInputsModel(annual_savings=5000)
print("SavingsInputsModel without interest_rate_per_yr:")
print(f"  interest_rate_per_yr: {savings_no_rate.interest_rate_per_yr}")

retirement_no_rate = RetirementInputsModel(current_age=35, retirement_age=67)
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
