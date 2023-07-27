import calendar
import csv
import datetime
import json

import xlwt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from userpreferences.models import UserPreference

from .models import Source, UserIncome

# Create your views here.


@login_required(login_url='authentication:login', redirect_field_name='next')
def getSource(request, source_id):
    sources = Source.objects.get(id=source_id, user=request.user)
    data = {
        'name': sources.name,
    }
    return JsonResponse(data)


@login_required(login_url='authentication:login', redirect_field_name='next')
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


@login_required(login_url='authentication:login', redirect_field_name='next')
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


@login_required(login_url='authentication:login', redirect_field_name='next')
def deleteIncome(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income deleted successfully')

    return redirect('income:home')


@login_required(login_url='authentication:login', redirect_field_name='next')
def expenseSourceLineSummary(request):
    todays_date = datetime.date.today()
    five_months_ago = todays_date - datetime.timedelta(days=30 * 5)
    # date__gte = greater than or equal to, (maiores ou iguais)
    # date__lte = less than or equal to, (menores ou iguais)
    incomes = UserIncome.objects.filter(
        date__gte=five_months_ago, date__lte=todays_date, user=request.user)

    finalrep = {}
    # Calculate the incomes for each month and store them in finalrep dictionary
    for income in incomes:
        month_year = f'{income.date.year}-{income.date.month:02}'
        finalrep[month_year] = finalrep.get(month_year, 0) + income.amount

    labels = []
    current_month = five_months_ago.month
    current_year = five_months_ago.year

    for i in range(6):  # Include the current month + 5 previous months
        month_name = calendar.month_name[current_month]
        labels.append(f'{month_name} {current_year}')
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1

    data = []

    for label in labels:
        month, year = label.split()
        month_number = list(calendar.month_name).index(month)
        month_year = f'{year}-{month_number:02}'
        amount = finalrep.get(month_year, 0)
        data.append(amount)

    return JsonResponse({'labels': labels, 'data': data})


@login_required(login_url='authentication:login', redirect_field_name='next')
def expenseSourceSummary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    incomes = UserIncome.objects.filter(date__gte=six_months_ago,
                                        date__lte=todays_date, user=request.user)
    finalrep = {}

    def get_income_source_amount(source_id):
        amount = 0
        filtered_by_source = incomes.filter(source_id=source_id)

        for item in filtered_by_source:
            amount += item.amount

        return amount

    for income in incomes:
        source_id = income.source.id
        source_name = income.source.name
        finalrep[source_name] = get_income_source_amount(source_id)

    return JsonResponse({'income_source_data': finalrep})


@login_required(login_url='authentication:login', redirect_field_name='next')
def exportCsv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Incomes' + \
        str(datetime.datetime.now())+'.csv'

    # módulo usada para criar um objeto gravador CSV
    writer = csv.writer(response)

    # gravar linhas de dados no arquivo CSV
    writer.writerow(['Amount', 'Description', 'Source', 'Date'])

    incomes = UserIncome.objects.filter(user=request.user)

    for income in incomes:
        writer.writerow([income.amount, income.description,
                         income.source, income.date])

    return response


@login_required(login_url='authentication:login', redirect_field_name='next')
def exportExcel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Incomes' + \
        str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Source', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = UserIncome.objects.filter(user=request.user).values_list(
        'amount', 'description', 'source', 'date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response
