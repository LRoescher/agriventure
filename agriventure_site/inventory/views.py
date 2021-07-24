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

from django.utils import dateparse

from .models import Transaction, TransactionComponent, Item, User, Customer, Warehouse, LaboratoryAnalysis, ScaleQuantity, WarehouseSlot

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
    print(Customer.objects.all().filter(name="Britta Röscher"))
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

    try:
        print(request.POST.get("transaction_type"))
    except:
        pass
    if "transaction_type" in request.POST.keys() and "plus" in request.POST.get("transaction_type"):
        print("Creating New Transaction")
        transaction_content = {k:request.POST.getlist(k) for k in request.POST.keys()}
        print(transaction_content)
        #calculate costs? Input??
        costs = 100

        #get customer by id
        delivered_by = Customer.objects.get(pk=transaction_content.get("delivered_by")[0].split("ID")[-1])

        #get user that created transaction
        done_by = User.objects.get(username=transaction_content.get("done_by")[0])

        #create all components
        components = []
        for i in range(len(transaction_content.get("item_type[]"))):

            #create laboratory Analysis
            laboratory_analysis = LaboratoryAnalysis(
            feuchte=float(transaction_content.get("feuchte[]")[i]),
            fallzahl = float(transaction_content.get("fallzahl[]")[i]),
            ausputz = float(transaction_content.get("ausputz[]")[i]),
            mutterkorn = float(transaction_content.get("mutterkorn[]")[i]),
            kleinbruch = float(transaction_content.get("kleinbruch[]")[i]),
            hlgewicht = float(transaction_content.get("hlgewicht[]")[i]),
            fremdgetreide = float(transaction_content.get("fremdgetreide[]")[i]),
            auswuchs = float(transaction_content.get("auswuchs[]")[i]),
            date = dateparse.parse_date(transaction_content.get("date")[0]),
            costs = costs,
            done_by = done_by,
            )

            laboratory_analysis.save()

            #create scale quantity
            scale_quantity = ScaleQuantity(
            brutto_weight= float(transaction_content.get("weight_brutto[]")[i]),
            scale_number = int(transaction_content.get("scale_id[]")[i]),
            vehicle_id = transaction_content.get("vehicle[]")[i],
            empty_weight = float(transaction_content.get("weight_empty[]")[i]),
            done_by = done_by,
            )
            scale_quantity.save()

            warehouse = Warehouse.objects.get(pk=transaction_content.get("warehouse[]")[i].split("ID")[-1])
            item = Item.objects.get(pk=transaction_content.get("item_type[]")[i].split("ID")[-1])
            c = TransactionComponent(
            item= item,
            laboratory_analysis = laboratory_analysis,
            vehicle_id = transaction_content.get("vehicle_id[]")[i],
            warehouse = warehouse,
            scale_quantity = scale_quantity
            )
            c.save()
            components.append(c)
            print(components)
            #update warehouse

            quantity = float(transaction_content.get("weight_brutto[]")[i]) - float(transaction_content.get("weight_empty[]")[i])
            existing = False
            for slot in warehouse.slots.all():
                if item.pk == slot.item.pk:
                    slot.quantity += float(transaction_content.get("weight_brutto[]")[i]) - float(transaction_content.get("weight_empty[]")[i])
                    slot.save()
                    existing = True
                    break
            if not existing:
                newslot = WarehouseSlot(item=item, quantity=quantity)
                newslot.save()
                warehouse.slots.add(newslot)
                warehouse.save()

        
        transaction = Transaction(
        date = dateparse.parse_date(transaction_content.get("date")[0]),
        time=dateparse.parse_time(transaction_content.get("time")[0]),
        costs = costs,
        delivered_by = delivered_by,
        done_by = done_by,
        transaction_type = "plus"
        )
        transaction.save()
        transaction.components.set(components)
        transaction.save()



    return render(request,'inventory/newentry.html', presets)

def list(request):
    try:
        objs = Transaction.objects.all()
    except:
        raise Http404("Error occured!")

    return render(request,'inventory/list.html',{'objs':objs})

