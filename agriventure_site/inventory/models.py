from django.db import models
import uuid

class Item(models.Model):
    crop_name = models.CharField(max_length=200) #Later by Crop class
    quantity = models.FloatField(null=True)

class Warehouse(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    items = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)


class TransactionComponent(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    laboratory_analysis = models.CharField(max_length=200)  # Later by LaboratoryAnalysis class
    vehicle_id = models.CharField(max_length=200)
    quantity = models.FloatField(null=True)

class Transaction(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, unique=True)
    tan = models.IntegerField(unique=True)
    date = models.DateField(null=True)
    costs = models.FloatField(null=True)
    delivered_by = models.CharField(null=True, max_length=200)

class InventorySystem(models.Model):
    warehouses = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    transactions = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)


