from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from .forms import GeneralInputsForm
from .full_descriptions import var_descriptions
from .models import GeneralInputsModel


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AlertsPageView(TemplateView):
    template_name = "pages/alerts.html"


class ButtonsPageView(TemplateView):
    template_name = "pages/buttons.html"


class BlankPageView(TemplateView):
    template_name = "pages/blank.html"


@login_required
def general_inputs_dashboard(request):
    general_inputs_models = GeneralInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        "pages/general_inputs.html",
        {"general_inputs": general_inputs_models},
    )


@login_required
def general_inputs_create(request):
    """This will validate/create a new general inputs item"""
    if request.method == "POST":
        print("POST request")
        print(f"{request.POST =}")
        form = GeneralInputsForm(request.POST)
        for field in form:
            print(field)

        if form.is_valid():
            print("Valid form")
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect("/general/")

        else:
            print("Not a valid form")
            for field in form:
                print(field)
            return render(
                request,
                "pages/inputs_create.html",
                {
                    "form": form,
                    "descriptions": var_descriptions,
                    "title": "Create New General Inputs",
                },
            )

    else:
        print("GET request")
        form = GeneralInputsForm()
        print(form)

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "Create New General Inputs",
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

            return redirect("general_inputs_dashboard")
    else:
        form = GeneralInputsForm(instance=general_inputs)

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "Edit General Inputs",
        },
    )


@login_required
def general_inputs_delete(request, pk):
    general_inputs = get_object_or_404(
        GeneralInputsModel, pk=pk, created_by=request.user
    )
    general_inputs.delete()

    return redirect("general_inputs_dashboard")
