from django.contrib import admin

from .models import (
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
)

admin.site.register(GeneralInputsModel)
admin.site.register(PaymentsInputsModel)
admin.site.register(RatesInputsModel)
admin.site.register(RetirementInputsModel)
admin.site.register(SavingsInputsModel)
