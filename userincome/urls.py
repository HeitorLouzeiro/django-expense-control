
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
    path('source/', views.Sources, name='source'),
    path('add/source/', views.AddSource, name='AddSource'),
    path('edit/source/', views.editSource, name='editSource'),
    path('delete/source/', views.deleteSource, name='deleteSource'),
    path('stats/income-source-line-summary/', views.expenseSourceLineSummary,
         name='incomeSourceLineSummary'),
    path('stats/income-source-summary/', views.expenseSourceSummary,
         name='incomeSourceSummary'),
    path('export-csv/', views.exportCsv, name='exportCsv'),
    path('export-excel/', views.exportExcel, name='exportExcel'),
]
