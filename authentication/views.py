import json
import threading

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
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
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


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
                    'norepley@heitorlouzeiro.com',
                    [email],

                )

                EmailThread(email).start()
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

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'Welcome ' +
                                     user.username + ' you are now logged in')
                    return redirect('expense:home')

                messages.error(request, 'Account is not active, please check your email box for account activation.')  # noqa
                return render(request, 'authentication/pages/login.html')

            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/pages/login.html')

        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/pages/login.html')


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('authentication:login')


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/pages/reset-password.html')

    def post(self, request):
        email = request.POST['email']

        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please supply a valid email address')
            return render(request, 'authentication/pages/reset-password.html', context)

        domain = get_current_site(request).domain
        user = User.objects.filter(email=email)

        if user.exists():
            email_contents = {
                'user': user[0],
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            }

            link = reverse('authentication:set-new-password', kwargs={
                'uidb64': email_contents['uid'], 'token': email_contents['token']
            })

            reset_url = 'http://' + domain + link

            email_subject = 'Password reset instructions'
            # email_body = 'Hi there, please the click below to reset your password\n' + reset_url,  # noqa

            email = EmailMessage(
                email_subject,
                'Hi there, please the click below to reset your password\n' + reset_url,
                'norepley@heitorlouzeiro.com',
                [email],
            )

            EmailThread(email).start()

        messages.success(
            request, 'We have sent you an email with instructions on how to reset your password.')
        return render(request, 'authentication/pages/reset-password.html')


class CompletePasswordReset(View):

    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(
                    request, 'Password reset link is invalid, please request a new one.')
                return render(request, 'authentication/pages/reset-password.html')
        except Exception:
            pass

        return render(request, 'authentication/pages/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        password = request.POST['password']
        confirmPassword = request.POST['ConfirmPassword']

        if password != confirmPassword:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/pages/set-new-password.html', context)

        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/pages/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(
                request, 'Password reset successful, you can now login with your new password.')
            return redirect('authentication:login')
        except Exception:
            messages.error(request, 'Something went wrong, please try again.')
            return render(request, 'authentication/pages/set-new-password.html', context)
