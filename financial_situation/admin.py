from django.contrib import admin

from .models import (
    FinancialInputs,
    TestCalc,
)


class InputsModelAdmin(admin.ModelAdmin):
    readonly_fields = ("modified_at",)


admin.site.register(FinancialInputs)
admin.site.register(TestCalc)
