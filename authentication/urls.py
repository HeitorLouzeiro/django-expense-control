from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import RegistrationView, UsernameValidation

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('registration/validate-username/', csrf_exempt(UsernameValidation.as_view()),
         name='validate-username'),
]
