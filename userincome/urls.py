
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'income'

urlpatterns = [
    path('', views.home, name='home'),
    path('add/income/', views.addIncome, name='addIncome'),
    path('edit/income/<int:id>/', views.editIncome, name='editIncome'),
    path('delete/income/<int:id>/', views.deleteIncome, name='deleteIncome'),
    path('search-incomes/', csrf_exempt(views.searchIncome), name='searchIncome'),
    path('get-source/<int:source_id>/',
         csrf_exempt(views.getSource), name='getSource'),
]
