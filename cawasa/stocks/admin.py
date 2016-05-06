from django.contrib import admin

from .models import Stock, Index

admin.site.register(Stock)
admin.site.register(Index)