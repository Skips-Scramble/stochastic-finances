from django.shortcuts import redirect, render

from .forms import SignupForm


def index(request):
    return render(request, "index.html")


def test_base(request):
    return render(request, "layouts/_base.html")


def home_page(request):
    return render(request, "pages/home.html")


def alerts_page(request):
    return render(request, "pages/alerts.html")


def buttons_page(request):
    return render(request, "pages/buttons.html")


def blank_page(request):
    return render(request, "pages/blank.html")


def account_login_page(request):
    return render(request, "pages/blank.html")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("/login/")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})
