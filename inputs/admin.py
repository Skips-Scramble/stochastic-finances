from django.contrib import admin

from .models import GeneralInputsModel, SavingsInputsModel, PaymentsInputsModel


class InputsModelAdmin(admin.ModelAdmin):
    readonly_fields = ("modified_at",)


admin.site.register(GeneralInputsModel, InputsModelAdmin)
admin.site.register(PaymentsInputsModel, InputsModelAdmin)
admin.site.register(SavingsInputsModel, InputsModelAdmin)
