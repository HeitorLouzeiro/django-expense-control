import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from validate_email import validate_email

from .utils import token_generator

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
                user.is_active = False
                user.save()

                domain = get_current_site(request).domain
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                link = reverse('authentication:activate', kwargs={
                    'uidb64': uidb64, 'token': token_generator.make_token(user)
                })

                activate_url = 'http://' + domain + link

                email_subject = 'Activate your account'
                email_body = 'Hi ' + user.username + ' Please use this link to verify your account\n' + activate_url  # noqa

                email = EmailMessage(
                    email_subject,
                    email_body,
                    'norepley@seycolon.com',
                    [email],

                )
                email.send(fail_silently=False)
                messages.success(request, 'Account created successfully')
                return render(request, 'authentication/pages/register.html')
            else:
                messages.error(request, 'Email is already taken')
                return render(request, 'authentication/pages/register.html')

        messages.success(
            request, 'Account created successfully, please check your email box for account activation.')  # noqa
        return render(request, 'authentication/pages/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('authentication:login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/pages/login.html')
