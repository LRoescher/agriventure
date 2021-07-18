from django.db import models
import uuid

class Item(models.Model):
    crop_name = models.CharField(max_length=200) #Later by Crop class
    quantity = models.FloatField(null=True)

    def __str__(self):
        return "{};{}".format(self.crop_name.__str__(), self.quantity.__str__())

class Warehouse(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    items = models.ManyToManyField(Item)

    def __str__(self):
        return self.name.__str__()


class TransactionComponent(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    laboratory_analysis = models.CharField(max_length=200)  # Later by LaboratoryAnalysis class
    vehicle_id = models.CharField(max_length=200)
    warehouse = models.ManyToManyField(Warehouse)

    def __str__(self):
        return "Posten: {} Menge: {}kg".format(*self.item.__str__().split(";"))

class Transaction(models.Model):
    tan = models.IntegerField(unique=True)
    date = models.DateTimeField(null=True)
    costs = models.FloatField(null=True)
    delivered_by = models.CharField(null=True, max_length=200)
    components = models.ManyToManyField(TransactionComponent)

    def __str__(self):
        return "{} | Name: {}".format(self.date.__str__(), self.delivered_by)

class InventorySystem(models.Model):
    warehouses = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    transactions = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)


