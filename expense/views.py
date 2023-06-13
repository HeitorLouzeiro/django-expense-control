from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


@login_required(login_url='authentication:login', redirect_field_name='next')
def home(request):
    return render(request, 'expense/pages/home.html')


@login_required(login_url='authentication:login', redirect_field_name='next')
def addExpense(request):
    return render(request, 'expense/pages/addExpense.html')
