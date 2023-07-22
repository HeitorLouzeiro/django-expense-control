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

from .models import Category, Expense

# Create your views here.


def getCategory(request, category_id):
    categories = Category.objects.get(id=category_id, user=request.user)
    data = {
        'name': categories.name,
    }
    return JsonResponse(data)


def searchExpense(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            Q(amount__istartswith=search_str) | Q(date__istartswith=search_str) |
            Q(description__icontains=search_str) | Q(
                category__name__icontains=search_str),
            user=request.user
        )
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='authentication:login', redirect_field_name='next')
def home(request):
    categories = Category.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    currency = UserPreference.objects.get(user=request.user).currency

    context = {
        'categories': categories,
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }

    return render(request, 'expense/pages/home.html', context)


@login_required(login_url='authentication:login', redirect_field_name='next')
def addExpense(request):
    template_name = 'expense/pages/addExpense.html'
    categories = Category.objects.filter(user=request.user)
    context = {
        'categories': categories,
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
        date = request.POST['expense_date']
        category = request.POST['category']

        category = Category.objects.get(id=category)

        if not description:
            messages.error(request, 'description is required')
            return render(request, template_name, context)

        Expense.objects.create(user=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('expense:home')


@login_required(login_url='authentication:login', redirect_field_name='next')
def editExpense(request, id):
    template_name = 'expense/pages/editExpense.html'
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.filter(user=request.user)

    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, template_name, context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, template_name, context)

        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        category = Category.objects.get(id=category)

        if not description:
            messages.error(request, 'description is required')
            return render(request, template_name, context)

        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.save()
        messages.success(request, 'Expense updated successfully')

        return redirect('expense:home')


@login_required(login_url='authentication:login', redirect_field_name='next')
def deleteExpense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense deleted successfully')

    return redirect('expense:home')


@login_required(login_url='authentication:login', redirect_field_name='next')
def expenseCategorySummary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(date__gte=six_months_ago,
                                      date__lte=todays_date, user=request.user)
    finalrep = {}

    def get_expense_category_amount(category_id):
        amount = 0
        filtered_by_category = expenses.filter(category_id=category_id)

        for item in filtered_by_category:
            amount += item.amount

        return amount

    for expense in expenses:
        category_id = expense.category.id
        category_name = expense.category.name
        finalrep[category_name] = get_expense_category_amount(category_id)

    return JsonResponse({'expense_category_data': finalrep})


@login_required(login_url='authentication:login', redirect_field_name='next')
def statsView(request):
    return render(request, 'expense/pages/stats.html')


@login_required(login_url='authentication:login', redirect_field_name='next')
def exportCsv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.csv'

    # módulo usada para criar um objeto gravador CSV
    writer = csv.writer(response)

    # gravar linhas de dados no arquivo CSV
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(user=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description,
                         expense.category, expense.date])

    return response


@login_required(login_url='authentication:login', redirect_field_name='next')
def exportExcel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(user=request.user).values_list(
        'amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response
