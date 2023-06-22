from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Category, Expense

# Create your views here.


@login_required(login_url='authentication:login', redirect_field_name='next')
def home(request):
    categories = Category.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    context = {
        'categories': categories,
        'expenses': expenses,
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


def deleteExpense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense deleted successfully')

    return redirect('expense:home')
