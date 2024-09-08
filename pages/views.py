import logging

import plotly.express as px
import plotly.graph_objects as go
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from . import stochastic_finances_func
from .forms import (
    GeneralInputsForm,
    PaymentsInputsForm,
    RatesInputsForm,
    RetirementInputsForm,
    SavingsInputsForm,
)
from .full_descriptions import var_descriptions
from .models import (
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
)
from .utils import ensure_active_inputs, model_to_dict

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    template_name = 'pages/home.html'


class AlertsPageView(TemplateView):
    template_name = 'pages/alerts.html'


class ButtonsPageView(TemplateView):
    template_name = 'pages/buttons.html'


class BlankPageView(TemplateView):
    template_name = 'pages/blank.html'


@login_required
def general_inputs_dashboard(request):
    general_inputs_models = GeneralInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        'pages/general_inputs.html',
        {'general_inputs': general_inputs_models},
    )


@login_required
def general_inputs_create(request):
    """This will validate/create a new general inputs item"""
    logger.debug('Creating general inputs')
    if request.method == 'POST':
        logger.debug('POST request')
        # print(f"{request.POST =}")
        form = GeneralInputsForm(request.POST)
        # for field in form:
        # print(field)

        if form.is_valid():
            # print("Valid form")
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect('/general/')

        else:
            # print("Not a valid form")
            # for field in form:
            # print(field)
            return render(
                request,
                'pages/inputs_create.html',
                {
                    'form': form,
                    'descriptions': var_descriptions,
                    'title': 'Create New General Inputs',
                },
            )

    else:
        logger.debug('GET request')
        form = GeneralInputsForm()
        # print(form)

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'Create New General Inputs',
        },
    )


@login_required
def general_inputs_edit(request, pk):
    """This will edit a general inputs item"""
    general_inputs = get_object_or_404(
        GeneralInputsModel, pk=pk, created_by=request.user
    )

    if request.method == 'POST':
        form = GeneralInputsForm(request.POST, instance=general_inputs)

        if form.is_valid():
            form.save()

            return redirect('general_inputs_dashboard')
    else:
        form = GeneralInputsForm(instance=general_inputs)

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'Edit General Inputs',
        },
    )


@login_required
def general_inputs_delete(request, pk):
    general_inputs = get_object_or_404(
        GeneralInputsModel, pk=pk, created_by=request.user
    )
    general_inputs.delete()

    return redirect('general_inputs_dashboard')


@login_required
def savings_inputs_dashboard(request):
    savings_inputs_models = SavingsInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        'pages/savings_inputs.html',
        {'savings_inputs': savings_inputs_models},
    )


@login_required
def savings_inputs_create(request):
    """This will validate/create a new savings inputs item"""
    if request.method == 'POST':
        form = SavingsInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect('/savings/')
    else:
        form = SavingsInputsForm()

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'New Savings Inputs',
        },
    )


@login_required
def savings_inputs_edit(request, pk):
    """This will edit a savings inputs item"""
    savings_inputs = get_object_or_404(
        SavingsInputsModel, pk=pk, created_by=request.user
    )

    if request.method == 'POST':
        form = SavingsInputsForm(request.POST, instance=savings_inputs)

        if form.is_valid():
            form.save()

            return redirect('/savings/')
    else:
        form = SavingsInputsForm(instance=savings_inputs)

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'Edit Savings Inputs',
        },
    )


@login_required
def savings_inputs_delete(request, pk):
    savings_inputs = get_object_or_404(
        SavingsInputsModel, pk=pk, created_by=request.user
    )
    savings_inputs.delete()

    return redirect('savings_inputs_dashboard')


@login_required
def payments_inputs_dashboard(request):
    payments_inputs_models = PaymentsInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        'pages/payments_inputs.html',
        {'payments_inputs': payments_inputs_models},
    )


@login_required
def payments_inputs_create(request):
    """This will validate/create a new payments inputs item"""
    if request.method == 'POST':
        form = PaymentsInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect('/payments/')
    else:
        form = PaymentsInputsForm()

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'New Payments Inputs',
        },
    )


@login_required
def payments_inputs_edit(request, pk):
    """This will edit a payments inputs item"""
    payments_inputs = get_object_or_404(
        PaymentsInputsModel, pk=pk, created_by=request.user
    )

    if request.method == 'POST':
        form = PaymentsInputsForm(request.POST, instance=payments_inputs)

        if form.is_valid():
            form.save()

            return redirect('/payments/')
    else:
        form = PaymentsInputsForm(instance=payments_inputs)

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'Edit payments Inputs',
        },
    )


@login_required
def payments_inputs_delete(request, pk):
    payments_inputs = get_object_or_404(
        PaymentsInputsModel, pk=pk, created_by=request.user
    )
    payments_inputs.delete()

    return redirect('payments_inputs_dashboard')


@login_required
def retirement_inputs_dashboard(request):
    retirement_inputs_models = RetirementInputsModel.objects.filter(
        created_by=request.user
    )

    return render(
        request,
        'pages/retirement_inputs.html',
        {'retirement_inputs': retirement_inputs_models},
    )


@login_required
def retirement_inputs_create(request):
    """This will validate/create a new retirement inputs item"""
    if request.method == 'POST':
        form = RetirementInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect('/retirement/')
    else:
        form = RetirementInputsForm()

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'New Retirement Inputs',
        },
    )


@login_required
def retirement_inputs_edit(request, pk):
    """This will edit a retirement inputs item"""
    retirement_inputs = get_object_or_404(
        RetirementInputsModel, pk=pk, created_by=request.user
    )

    if request.method == 'POST':
        form = RetirementInputsForm(request.POST, instance=retirement_inputs)

        if form.is_valid():
            form.save()

            return redirect('/retirement/')
    else:
        form = RetirementInputsForm(instance=retirement_inputs)

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'Edit retirement Inputs',
        },
    )


@login_required
def retirement_inputs_delete(request, pk):
    retirement_inputs = get_object_or_404(
        RetirementInputsModel, pk=pk, created_by=request.user
    )
    retirement_inputs.delete()

    return redirect('retirement_inputs_dashboard')


@login_required
def rates_inputs_dashboard(request):
    rates_inputs_models = RatesInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        'pages/rates_inputs.html',
        {'rates_inputs': rates_inputs_models},
    )


@login_required
def rates_inputs_create(request):
    """This will validate/create a new rates inputs item"""
    if request.method == 'POST':
        form = RatesInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect('/rates/')
    else:
        form = RatesInputsForm()

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'New rates Inputs',
        },
    )


@login_required
def rates_inputs_edit(request, pk):
    """This will edit a rates inputs item"""
    rates_inputs = get_object_or_404(RatesInputsModel, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = RatesInputsForm(request.POST, instance=rates_inputs)

        if form.is_valid():
            form.save()

            return redirect('/rates/')
    else:
        form = RatesInputsForm(instance=rates_inputs)

    return render(
        request,
        'pages/inputs_create.html',
        {
            'form': form,
            'descriptions': var_descriptions,
            'title': 'Edit rates Inputs',
        },
    )


@login_required
def rates_inputs_delete(request, pk):
    rates_inputs = get_object_or_404(RatesInputsModel, pk=pk, created_by=request.user)
    rates_inputs.delete()

    return redirect('rates_inputs_dashboard')


@login_required
def calculations(request):
    """This will run the financial calculations"""
    if request.method == 'POST':
        print('Post request')

    else:
        print('Get request')
        bad_active_list = []
        general_inputs_model = GeneralInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )

        if ensure_active_inputs(general_inputs_model, 1):
            general_inputs_dict = model_to_dict(general_inputs_model[0], 'general')
            print(f'{general_inputs_dict =}')
        else:
            bad_active_list.append('General')

        savings_inputs_model = SavingsInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )

        if ensure_active_inputs(savings_inputs_model, 1):
            savings_inputs_dict = model_to_dict(savings_inputs_model[0], 'savings')
            print(f'{savings_inputs_dict =}')
        else:
            bad_active_list.append('Savings')

        payments_inputs_model = PaymentsInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        payments_list = []
        for payment in payments_inputs_model:
            print(model_to_dict(payment, 'payments'))
            payments_list.append(model_to_dict(payment, 'payments'))
        print(f'{payments_list = }')

        retirement_inputs_model = RetirementInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        if ensure_active_inputs(retirement_inputs_model, 1):
            retirement_inputs_dict = model_to_dict(
                retirement_inputs_model[0], 'retirement'
            )
            print(f'{retirement_inputs_dict =}')
        else:
            bad_active_list.append('Retirement')

        rates_inputs_model = RatesInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        if ensure_active_inputs(rates_inputs_model, 1):
            rates_inputs_dict = model_to_dict(rates_inputs_model[0], 'rates')
            print(f'{rates_inputs_dict =}')
        else:
            bad_active_list.append('Rates')
        if bad_active_list:
            print('There were some bad active inputs')
            return render(
                request,
                'pages/non_active.html',
                {
                    'errors': bad_active_list,
                },
            )

    full_dict = {
        **{'name': 'Test Scenario'},
        **general_inputs_dict,
        **savings_inputs_dict,
        **{'payment_items': payments_list},
        **retirement_inputs_dict,
        **rates_inputs_dict,
    }

    print(f'full_dict is {full_dict}')
    # print(f'base_bills is {full_dict['base_monthly_bills']}')

    (total_savings_df, total_retirement_df, total_outputs_df) = (
        stochastic_finances_func.main(full_dict)
    )

    results_dict = {}
    for age in range(40, 105, 5):
        print(f'Processing calc for age {age}')
        print(total_savings_df.head())
        savings_at_age = total_savings_df.loc[
            lambda df: (df.age_yrs == age) & (df.age_mos == 0)
        ]['avg'].iat[0]
        print(f'{savings_at_age = }')

        retirement_at_age = total_retirement_df.loc[
            lambda df: (df.age_yrs == age) & (df.age_mos == 0)
        ]['avg'].iat[0]
        print(f'{retirement_at_age = }')

        results_dict[age] = [
            f'Average savings at age {age} is ${savings_at_age:,.0f}',
            f'Average retirement at age {age} is ${retirement_at_age:,.0f}',
        ]
    print(f'{results_dict = }')
    print('')
    # print(val for val in results_dict.values())

    savings_retirement_fig = px.line(
        total_outputs_df, x='age_yrs', y='avg', color='account_type', height=600
    )
    savings_retirement_fig.update_xaxes(title_text='Age (years)', dtick=5)
    savings_retirement_fig.update_yaxes(title_text='Amount')
    savings_retirement_fig_html = savings_retirement_fig.to_html()
    print(f'savings_retirement_fig_html type: {type(savings_retirement_fig_html)}')

    table_view = (
        total_outputs_df[['age_yrs', 'account_type', 'avg']]
        .pivot(index='age_yrs', columns='account_type', values='avg')
        .reset_index()
        # .to_html(
        #     classes="table table-hover table-primary table-striped table-bordered",
        #     columns=["age_yrs", "savings", "retirement", "total"],
        #     index=False,
        #     index_names=False,
        # )
    )
    print('')
    print(f'table_view type is {type(table_view)}')

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(table_view.columns),
                    fill_color='paleturquoise',
                    align='left',
                ),
                cells=dict(
                    values=[
                        table_view.age_yrs,
                        table_view.savings,
                        table_view.retirement,
                        table_view.total,
                    ],
                    fill_color='lavender',
                    align='left',
                ),
            )
        ],
    )

    # fig.show()

    return render(
        request,
        'pages/calculations.html',
        {
            'chart': savings_retirement_fig_html,
            'table': fig.to_html(),
        },
    )
