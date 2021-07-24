from django.db import models
import uuid
from django.contrib.auth.models import User

class Address(models.Model):
    street = models.CharField(max_length=200)
    plz = models.IntegerField(unique=True)
    city = models.CharField(max_length=200)

    def __str__(self):
        return "{},\n{},\n{}".format(self.street, self.plz, self.city)


class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200, unique=True)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True)
    telephone =models.CharField(max_length=200, unique=True)
    customer_type = models.CharField(max_length=200,
                                        choices=[("company", "Agrarbetrieb"), ("private", "Privat")],
                                        default=("company", "Agrarbetrieb"))
    def __str__(self):
        return "{}, {}; {} ID{}".format(self.name, self.first_name, self.address.city, self.pk)


class Item(models.Model):
    crop_name = models.CharField(max_length=200) #Later by Crop class

    def __str__(self):
        return "{} ID{}".format(self.crop_name.__str__(), self.pk)

class WarehouseSlot(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField(null=True)

    def __str__(self):
        return "{} {} ID{}".format(self.item, self.quantity, self.pk)

class Warehouse(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    slots = models.ManyToManyField(WarehouseSlot)

    def __str__(self):
        return "{} ID{}".format(self.name.__str__(), self.pk)

class LaboratoryAnalysis(models.Model):
    feuchte = models.FloatField(null=True)
    fallzahl = models.FloatField(null=True)
    ausputz = models.FloatField(null=True)
    mutterkorn = models.FloatField(null=True)
    kleinbruch = models.FloatField(null=True)
    hlgewicht = models.FloatField(null=True)
    fremdgetreide = models.FloatField(null=True)
    auswuchs = models.FloatField(null=True)

    date = models.DateTimeField(null=True)
    costs = models.FloatField(null=True)
    done_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{} ID{}".format(self.date.__str__(), self.pk)

class ScaleQuantity(models.Model):
    brutto_weight = models.FloatField(null=True)
    scale_number = models.IntegerField()
    vehicle_id = models.CharField(max_length=200)
    empty_weight = models.FloatField(null=True)
    done_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{}; {} ID{}".format(self.vehicle_id, self.brutto_weight, self.pk)


class TransactionComponent(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    laboratory_analysis = models.OneToOneField(LaboratoryAnalysis, null=True, on_delete=models.SET_NULL)
    vehicle_id = models.CharField(max_length=200)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    scale_quantity = models.OneToOneField(ScaleQuantity,null = True,  on_delete=models.SET_NULL)

    def __str__(self):
        return "Posten: {} Menge: {}kg ID{}".format(self.item.crop_name, str(self.scale_quantity.brutto_weight - self.scale_quantity.brutto_weight), self.pk)

class Transaction(models.Model):
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    costs = models.FloatField(null=True)
    delivered_by = models.ForeignKey(Customer, on_delete=models.CASCADE)
    done_by = models.ForeignKey(User, on_delete=models.CASCADE)
    components = models.ManyToManyField(TransactionComponent)
    main_vehicle = models.CharField(max_length=200, null=True)
    transaction_type = models.CharField(max_length=200, choices=[("plus", "Zugang"), ("minus", "Abgang"), ("flux", "Umlagerung")], default=("plus", "Zugang"))

    def __str__(self):
        return "{} | Name: {} ID{}".format(self.date.__str__(), self.delivered_by.last_name, self.pk)

class InventorySystem(models.Model):
    warehouses = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    transactions = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)


