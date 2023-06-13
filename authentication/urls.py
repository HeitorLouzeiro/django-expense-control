from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import (EmailValidationView, LoginView, LogoutView,
                    RegistrationView, UsernameValidationView, VerificationView)

app_name = 'authentication'

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registration/validate-username/', csrf_exempt(UsernameValidationView.as_view()),
         name='validate-username'),

    path('registration/validate-email/', csrf_exempt(EmailValidationView.as_view()),
         name='validate-email'),
    path('registration/activate/<uidb64>/<token>/',
         VerificationView.as_view(), name='activate'),

]
