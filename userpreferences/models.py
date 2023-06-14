from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class UserPreference(models.Model):
    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE)
    currency = models.CharField(
        max_length=255, null=True, blank=True, default='USD')

    def __str__(self):
        return str(self.user) + 's' + ' preferences'
