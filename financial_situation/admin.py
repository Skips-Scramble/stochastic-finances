from django.contrib import admin

from .models import FinancialInputs, GeneralInputsModel, SavingsInputsModel, TestCalc

admin.site.register(TestCalc)
admin.site.register(FinancialInputs)
admin.site.register(GeneralInputsModel)
admin.site.register(SavingsInputsModel)
