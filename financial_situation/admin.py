from django.contrib import admin

from .models import (
    FinancialInputs,
    GeneralInputsModel,
    PaymentsInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
    TestCalc,
)

admin.site.register(TestCalc)
admin.site.register(FinancialInputs)
admin.site.register(GeneralInputsModel)
admin.site.register(SavingsInputsModel)
admin.site.register(RetirementInputsModel)
admin.site.register(PaymentsInputsModel)
