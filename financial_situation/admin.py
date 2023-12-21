from django.contrib import admin

from .models import (
    FinancialInputs,
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
    TestCalc,
)

admin.site.register(FinancialInputs)
admin.site.register(GeneralInputsModel)
admin.site.register(PaymentsInputsModel)
admin.site.register(RatesInputsModel)
admin.site.register(RetirementInputsModel)
admin.site.register(SavingsInputsModel)
admin.site.register(TestCalc)
