import django_tables2 as tables
from django_tables2 import TemplateColumn
from .models import Transaction


class TransactionTable(tables.Table):
    class Meta:
        model = Transaction
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'date',
            'time',
            'transaction_type',
            'delivered_by',
            'done_by',
            'components',
            'costs',
            'Lieferschein'
        )
    Lieferschein = TemplateColumn(template_name='inventory/tables/list_generate_column_template.html')