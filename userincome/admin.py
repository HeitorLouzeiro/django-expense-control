from django.contrib import admin

from .models import Source, UserIncome

# Register your models here.

admin.site.register(Source)
admin.site.register(UserIncome)
