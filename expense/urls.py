from django.urls import path

from . import views

app_name = 'expense'

urlpatterns = [
    path('', views.home, name='home'),
    path('add/expense/', views.addExpense, name='addExpense'),
    path('edit/expense/<int:id>/', views.editExpense, name='editExpense'),
    path('delete/expense/<int:id>/', views.deleteExpense, name='deleteExpense'),
]
