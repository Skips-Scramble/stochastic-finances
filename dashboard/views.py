from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# from financial_situation.forms import GeneralInputsForm
# from financial_situation.models import GeneralInputsModel


# @login_required
# def general_inputs_dashboard(request):
#     general_inputs_models = GeneralInputsModel.objects.filter(created_by=request.user)

#     return render(
#         request,
#         "dashboard/general_inputs_dashboard.html",
#         {"general_inputs": general_inputs_models},
#     )
