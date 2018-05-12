from django.contrib import admin

from django.contrib.admin import register

# Register your models here.
from .models import Seed


@register(Seed)
class SeedAdmin(admin.ModelAdmin):
    pass
