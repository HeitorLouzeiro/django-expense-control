
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import UserPreference


@receiver(user_logged_in)
def create_user_preference(sender, request, user, **kwargs):
    try:
        UserPreference.objects.get(user=user)
    except UserPreference.DoesNotExist:
        UserPreference.objects.create(user=user, currency='USD')
