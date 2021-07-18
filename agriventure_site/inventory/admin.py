from django.contrib import admin

from .models import Transaction, Warehouse, Item, TransactionComponent

admin.site.register(Transaction)
admin.site.register(Warehouse)
admin.site.register(Item)
admin.site.register(TransactionComponent)