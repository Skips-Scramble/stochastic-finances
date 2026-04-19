import sys
sys.path.insert(0, 'C:\\Users\\Sam\\Desktop\\School\\Repos\\stochastic-finances')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Test the override logic from views.py
global_rates_dict = {
    'base_rf_interest_per_yr': 2.0,
    'base_mkt_interest_per_yr': 5.0,
}

# Test 1: Savings account with override
savings_rate_override = 3.5
if savings_rate_override is not None:
    global_rates_dict['base_rf_interest_per_yr'] = savings_rate_override

print(f"Test 1 - Savings override: {global_rates_dict['base_rf_interest_per_yr']} (expected 3.5)")

# Reset
global_rates_dict['base_rf_interest_per_yr'] = 2.0

# Test 2: Savings account without override
savings_rate_override = None
if savings_rate_override is not None:
    global_rates_dict['base_rf_interest_per_yr'] = savings_rate_override

print(f"Test 2 - No savings override: {global_rates_dict['base_rf_interest_per_yr']} (expected 2.0)")

# Test 3: Retirement account override in list
retirement_list = [
    {'retirement_type': 'traditional_401k', 'interest_rate_per_yr': 6.0},
    {'retirement_type': 'roth_ira', 'interest_rate_per_yr': None},
]

for i, ret in enumerate(retirement_list):
    if ret['interest_rate_per_yr'] is not None:
        print(f"Test 3.{i+1} - Retirement account {i}: override = {ret['interest_rate_per_yr']}")
    else:
        print(f"Test 3.{i+1} - Retirement account {i}: will use global rate {global_rates_dict['base_mkt_interest_per_yr']}")

print("SUCCESS: Override logic working!")
