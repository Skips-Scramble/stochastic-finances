from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GeneralInputsForm, SavingsInputsForm
from .models import GeneralInputsModel, SavingsInputsModel


@login_required
def general_inputs_dashboard(request):
    general_inputs_models = GeneralInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        "inputs/general_inputs.html",
        {"general_inputs": general_inputs_models},
    )


@login_required
def general_inputs_create(request):
    """This will validate/create a new general inputs item"""
    if request.method == "POST":
        print("POST request")
        form = GeneralInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect("/inputs/general/")
    else:
        print("GET request")
        form = GeneralInputsForm()
        print(form)

    return render(
        request,
        "inputs/inputs_create.html",
        {
            "form": form,
            "title": "New General Inputs",
        },
    )


@login_required
def general_inputs_edit(request, pk):
    """This will edit a general inputs item"""
    general_inputs = get_object_or_404(
        GeneralInputsModel, pk=pk, created_by=request.user
    )

    if request.method == "POST":
        form = GeneralInputsForm(request.POST, instance=general_inputs)

        if form.is_valid():
            form.save()

            return redirect("inputs:general_inputs_dashboard")
    else:
        form = GeneralInputsForm(instance=general_inputs)

    return render(
        request,
        "inputs/inputs_create.html",
        {
            "form": form,
            "title": "Edit General Inputs",
        },
    )


@login_required
def general_inputs_delete(request, pk):
    general_inputs = get_object_or_404(
        GeneralInputsModel, pk=pk, created_by=request.user
    )
    general_inputs.delete()

    return redirect("inputs:general_inputs_dashboard")


@login_required
def savings_inputs_dashboard(request):
    savings_inputs_models = SavingsInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        "inputs/savings_inputs.html",
        {"savings_inputs": savings_inputs_models},
    )


@login_required
def savings_inputs_create(request):
    """This will validate/create a new savings inputs item"""
    if request.method == "POST":
        form = SavingsInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect("/inputs/savings/")
    else:
        form = SavingsInputsForm()

    return render(
        request,
        "inputs/inputs_create.html",
        {
            "form": form,
            "title": "New Savings Inputs",
        },
    )


@login_required
def savings_inputs_edit(request, pk):
    """This will edit a savings inputs item"""
    savings_inputs = get_object_or_404(
        SavingsInputsModel, pk=pk, created_by=request.user
    )

    if request.method == "POST":
        form = SavingsInputsForm(request.POST, instance=savings_inputs)

        if form.is_valid():
            form.save()

            return redirect("/inputs/savings/")
    else:
        form = SavingsInputsForm(instance=savings_inputs)

    return render(
        request,
        "inputs/inputs_create.html",
        {
            "form": form,
            "title": "Edit Savings Inputs",
        },
    )


@login_required
def savings_inputs_delete(request, pk):
    savings_inputs = get_object_or_404(
        SavingsInputsModel, pk=pk, created_by=request.user
    )
    savings_inputs.delete()

    return redirect("inputs:savings_inputs_dashboard")
