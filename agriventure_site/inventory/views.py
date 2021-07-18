from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt,csrf_protect

from django.views.generic import ListView

from django_tables2 import SingleTableView
from .tables import TransactionTable
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from .models import Transaction

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
    temp_item = {'delivered_by':['Röscher']}
    if "new_component" in request.POST.keys():
        print(request.POST)
        temp_item = {'date_time': request.POST.get('datetime'),
                     'delivered_by':request.POST.get('delivered_by'),
                     'entry_type': 'true' if request.POST.get('entry_type') == 'on' else 'false'
                     }

    return render(request,'inventory/newentry.html',{'temp_item':temp_item})

def list(request):
    try:
        objs = Transaction.objects.all()
    except:
        raise Http404("Error occured!")

    return render(request,'inventory/list.html',{'objs':objs})

