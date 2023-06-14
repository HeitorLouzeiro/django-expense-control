from django.urls import path

from . import views

app_name = 'userpreferences'

urlpatterns = [
    path('preferences/', views.preferences, name='preferences'),
]
