from django.contrib import admin

from .models import Transaction, Warehouse, Item, TransactionComponent, LaboratoryAnalysis, WarehouseSlot, ScaleQuantity, Customer, Address

admin.site.register(Transaction)
admin.site.register(Warehouse)
admin.site.register(Item)
admin.site.register(TransactionComponent)
admin.site.register(LaboratoryAnalysis)
admin.site.register(WarehouseSlot)
admin.site.register(ScaleQuantity)
admin.site.register(Customer)
admin.site.register(Address)