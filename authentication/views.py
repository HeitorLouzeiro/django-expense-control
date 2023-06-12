import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from validate_email import validate_email

# Create your views here.


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)  # noqa

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Username is already taken'}, status=409)  # noqa

        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)  # noqa

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Email is already taken'}, status=409)  # noqa

        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/pages/register.html')

    def post(self, request):
        # Get user data
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'fieldValues': request.POST
        }

        # Validate user data
        # username exists
        if not User.objects.filter(username=username).exists():
            # email exists
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/pages/register.html', context)  # noqa
                # Create user account
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.save()
                messages.success(request, 'Account created successfully')
                return render(request, 'authentication/pages/register.html')
            else:
                messages.error(request, 'Email is already taken')
                return render(request, 'authentication/pages/register.html')

        messages.success(request, 'Account created successfully')
        return render(request, 'authentication/pages/register.html')
