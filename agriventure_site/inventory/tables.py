import django_tables2 as tables
from django_tables2 import TemplateColumn
from .models import Transaction, Warehouse

class WarehouseTable(tables.Table):
    class Meta:
        model = Warehouse
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'name',
            'location',
            'slots'
        )
    slots = tables.ManyToManyColumn(verbose_name="Bestand")
    name = tables.Column(verbose_name="Bezeichnung")
    location = tables.Column(verbose_name="Ort")



class TransactionTable(tables.Table):
    class Meta:
        model = Transaction
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'pk',
            'date',
            'time',
            'transaction_type',
            'delivered_by',
            'done_by',
            'components',
            'costs',
        )

    pk = TemplateColumn(verbose_name='Lieferschein NR.', template_name='inventory/tables/list_generate_column_template.html')
    date = tables.Column(verbose_name= 'Datum' )
    time = tables.Column(verbose_name='Uhrzeit')
    transaction_type = tables.Column(verbose_name='Art')
    delivered_by = tables.Column(verbose_name='Für')
    done_by = tables.Column(verbose_name='Von')
    components = tables.ManyToManyColumn(verbose_name="Komponenten")
    costs = tables.Column(verbose_name='Kosten')