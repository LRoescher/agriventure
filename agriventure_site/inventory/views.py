from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt,csrf_protect

from django.views.generic import ListView

from django_tables2 import SingleTableView
from .tables import TransactionTable
from django_filters.views import FilterView
from django.views.generic import CreateView
from django_tables2.views import SingleTableMixin

from django.db.models import Model

from .models import Transaction, TransactionComponent, Item, User, Customer, Warehouse, LaboratoryAnalysis

import django_filters

class TransactioFilter(django_filters.FilterSet):
    class Meta:
        model = Transaction
        fields = ['date', 'delivered_by']

class InventoryListView(SingleTableMixin, FilterView):

    model = Transaction
    table_class = TransactionTable
    template_name = 'inventory/list.html'

    filterset_class = TransactioFilter

class TransactionCreateView(CreateView):
    model = Transaction

    fields = (
    'tan',
    'date' ,
    'costs' ,
    'delivered_by',
    'done_by' ,
    'components' ,
    'transaction_type' ,
              )


@csrf_exempt
def index(request):

    try:
        template = loader.get_template('inventory/index.html')
    except:
        raise Http404("Error occured!")

    if request.method == "POST":
        if 'new_transactions'in request.POST.keys():
            return redirect('newentry/')
        if 'list_transactions'in request.POST.keys():
            return redirect('list/')

    return HttpResponse(template.render())

@csrf_exempt
def newentry(request):
    #get locals for form
    delivered_by_preset = Customer.objects.all()
    done_by_preset = User.objects.all()
    item_preset = Item.objects.all()
    warehouse_preset = Warehouse.objects.all()

    # get attributes from laboratory analysis and filter out meta
    laboratory_attributes = set(dir(LaboratoryAnalysis)).difference(set(dir(Model)))
    laboratory_attributes = [e for e in laboratory_attributes if not "_" in e]
    for e in ['DoesNotExist', 'id', 'objects', 'MultipleObjectsReturned', 'transactioncomponent', 'date', 'costs']:
        laboratory_attributes.remove(e)

    presets = {
        'delivered_by_preset': delivered_by_preset,
        'done_by_preset':done_by_preset,
        'item_preset':item_preset,
        'warehouse_preset':warehouse_preset,
        'laboratory_attributes':laboratory_attributes
    }

    print(request.POST)

    if "new_component" in request.POST.keys():
        item = Item.objects.create(crop_name = "ddfwf")
    if "new_component" in request.POST.keys():
        print(request.POST)
        temp_item = {'date_time': request.POST.get('datetime'),
                     'delivered_by':request.POST.get('delivered_by'),
                     'entry_type': 'true' if request.POST.get('entry_type') == 'on' else 'false'
                     }

    return render(request,'inventory/newentry.html', presets)

def list(request):
    try:
        objs = Transaction.objects.all()
    except:
        raise Http404("Error occured!")

    return render(request,'inventory/list.html',{'objs':objs})

