# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Sources'


class UserIncome(models.Model):
    amount = models.FloatField()
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    source = models.ForeignKey('Source', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.description + ' - ' + str(self.amount)

    class Meta:
        ordering = ['-date']
