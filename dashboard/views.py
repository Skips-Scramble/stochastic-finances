from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from financial_situation.models import FinancialInputs


@login_required
def index(request):
    financial_inputs = FinancialInputs.objects.filter(created_by=request.user)

    return render(
        request,
        "dashboard/index.html",
        {
            "financial_inputs": financial_inputs,
        },
    )
