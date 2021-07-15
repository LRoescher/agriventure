from django.contrib import admin

from .models import Transaction, Warehouse, Item

admin.site.register(Transaction)
admin.site.register(Warehouse)
admin.site.register(Item)