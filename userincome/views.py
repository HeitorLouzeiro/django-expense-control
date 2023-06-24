import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render

from userpreferences.models import UserPreference

from .models import Source, UserIncome

# Create your views here.


def getSource(request, source_id):
    sources = Source.objects.get(id=source_id, user=request.user)
    data = {
        'name': sources.name,
    }
    return JsonResponse(data)


def searchIncome(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            Q(amount__istartswith=search_str) | Q(date__istartswith=search_str) |
            Q(description__icontains=search_str) | Q(
                source__name__icontains=search_str),
            user=request.user
        )
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='authentication:login', redirect_field_name='next')
def home(request):
    source = Source.objects.filter(user=request.user)
    incomes = UserIncome.objects.filter(user=request.user)
    paginator = Paginator(incomes, 10)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    currency = UserPreference.objects.get(user=request.user).currency

    context = {
        'source': source,
        'incomes': incomes,
        'page_obj': page_obj,
        'currency': currency
    }

    return render(request, 'income/pages/home.html', context)


@login_required(login_url='authentication:login', redirect_field_name='next')
def addIncome(request):
    template_name = 'income/pages/addIncome.html'
    sources = Source.objects.filter(user=request.user)
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, template_name, context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, template_name, context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        source = Source.objects.get(id=source)

        if not description:
            messages.error(request, 'description is required')
            return render(request, template_name, context)

        UserIncome.objects.create(user=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Income saved successfully')

        return redirect('income:home')


def editIncome(request, id):
    template_name = 'income/pages/editIncome.html'
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.filter(user=request.user)

    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, template_name, context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, template_name, context)

        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        source = Source.objects.get(id=source)

        if not description:
            messages.error(request, 'description is required')
            return render(request, template_name, context)

        income.amount = amount
        income.date = date
        income.source = source
        income.description = description
        income.save()
        messages.success(request, 'Income updated successfully')

        return redirect('income:home')


def deleteIncome(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income deleted successfully')

    return redirect('income:home')
