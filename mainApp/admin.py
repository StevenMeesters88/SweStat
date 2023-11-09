from django.contrib import admin
from .models import VisitorData


# Register your models here.
@admin.register(VisitorData)
class VisitorDataAdmin(admin.ModelAdmin):
    list_display = ["ip", "datetime"]
