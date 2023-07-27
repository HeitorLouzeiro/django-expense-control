
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'expense'

urlpatterns = [
    path('', views.home, name='home'),
    path('add/expense/', views.addExpense, name='addExpense'),
    path('edit/expense/<int:id>/', views.editExpense, name='editExpense'),
    path('delete/expense/<int:id>/', views.deleteExpense, name='deleteExpense'),
    path('search-expenses/', csrf_exempt(views.searchExpense), name='searchExpense'),
    path('get-category/<int:category_id>/',
         csrf_exempt(views.getCategory), name='getCategory'),
    path('categories/', views.Categories, name='categories'),
    path('add/category/', views.addCategory, name='addCategory'),
    path('edit/category/', views.editCategory, name='editCategory'),
    path('delete/category/', views.deleteCategory, name='deleteCategory'),
    path('stats/expense-category-summary/', views.expenseCategorySummary,
         name='expenseCategorySummary'),
    path('stats/expense-category-line-summary/', views.expenseCategoryLineSummary,
         name='expenseCategoryLineSummary'),
    path('export-csv/', views.exportCsv, name='exportCsv'),
    path('export-excel/', views.exportExcel, name='exportExcel'),
]
