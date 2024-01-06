from django.contrib import admin

from .models import (
    FinancialInputs,
    RatesInputsModel,
    RetirementInputsModel,
    TestCalc,
)


class InputsModelAdmin(admin.ModelAdmin):
    readonly_fields = ("modified_at",)


admin.site.register(FinancialInputs)
admin.site.register(RatesInputsModel, InputsModelAdmin)
admin.site.register(RetirementInputsModel, InputsModelAdmin)
admin.site.register(TestCalc)
