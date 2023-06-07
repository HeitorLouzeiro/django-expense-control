from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'expense/pages/home.html')


def addExpense(request):
    return render(request, 'expense/pages/addExpense.html')
