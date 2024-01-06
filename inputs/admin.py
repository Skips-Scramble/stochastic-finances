from django.contrib import admin

from .models import (
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
)


class InputsModelAdmin(admin.ModelAdmin):
    readonly_fields = ("modified_at",)


admin.site.register(GeneralInputsModel, InputsModelAdmin)
admin.site.register(PaymentsInputsModel, InputsModelAdmin)
admin.site.register(RatesInputsModel, InputsModelAdmin)
admin.site.register(RetirementInputsModel, InputsModelAdmin)
admin.site.register(SavingsInputsModel, InputsModelAdmin)
