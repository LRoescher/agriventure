from django.db import models


class Transaction(models.Model):
    transaction_id = models.IntegerField(unique=True)
    transaction_date = models.DateTimeField('Zeitpunkt des Waren Ein/Ausgangs')

    def __str__(self):
        return "lieferung_{}".format(self.transaction_id)


class LaboratoryAnalysis(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    humidity = models.FloatField()
