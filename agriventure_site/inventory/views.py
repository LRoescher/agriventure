from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt,csrf_protect

from .tables import TransactionTable, WarehouseTable
from django_filters.views import FilterView
from django.views.generic import CreateView
from django_tables2.views import SingleTableMixin

from django.db.models import Model

from django.utils import dateparse

from .models import Transaction, TransactionComponent, Item, User, Customer, Warehouse, LaboratoryAnalysis, ScaleQuantity, WarehouseSlot

import django_filters

import bs4
import datetime
import pdfkit

import os
import mimetypes

class TransactioFilter(django_filters.FilterSet):
    class Meta:
        model = Transaction
        fields = ['date']

class WarehouseListView(SingleTableMixin, FilterView):
    model = Warehouse
    table_class = WarehouseTable
    template_name = 'inventory/stock.html'

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
            return redirect('list/?sort=-pk')

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
    if "transaction_type" in request.POST.keys():
        if "plus" in request.POST.get("transaction_type"):
            tan_type = "plus"
        if "minus" in request.POST.get("transaction_type"):
            tan_type = "minus"
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
        quantities = []
        lab_analysis = []
        for i in range(len(transaction_content.get("item_type[]"))):

            #create laboratory Analysis
            laboratory_analysis = LaboratoryAnalysis(
            feuchte=float(transaction_content.get("feuchte[]")[i].replace(',','.')),
            fallzahl = float(transaction_content.get("fallzahl[]")[i].replace(',','.')),
            ausputz = float(transaction_content.get("ausputz[]")[i].replace(',','.')),
            mutterkorn = float(transaction_content.get("mutterkorn[]")[i].replace(',','.')),
            kleinbruch = float(transaction_content.get("kleinbruch[]")[i].replace(',','.')),
            hlgewicht = float(transaction_content.get("hlgewicht[]")[i].replace(',','.')),
            fremdgetreide = float(transaction_content.get("fremdgetreide[]")[i].replace(',','.')),
            auswuchs = float(transaction_content.get("auswuchs[]")[i].replace(',','.')),
            date = dateparse.parse_date(transaction_content.get("date")[0]),
            costs = costs,
            done_by = done_by,
            )

            laboratory_analysis.save()
            lab_analysis.append(laboratory_analysis)

            #create scale quantity
            scale_quantity = ScaleQuantity(
            brutto_weight= float(transaction_content.get("weight_brutto[]")[i].replace(',','.')),
            scale_number = int(transaction_content.get("scale_id[]")[i]),
            vehicle_id = transaction_content.get("vehicle[]")[i],
            empty_weight = float(transaction_content.get("weight_empty[]")[i].replace(',','.')),
            done_by = done_by,
            )
            scale_quantity.save()
            quantities.append(scale_quantity)

            warehouse = Warehouse.objects.get(pk=transaction_content.get("warehouse[]")[i].split("ID")[-1])
            item = Item.objects.get(pk=transaction_content.get("item_type[]")[i].split("ID")[-1])
            c = TransactionComponent(
            item= item,
            laboratory_analysis = laboratory_analysis,
            vehicle_id = transaction_content.get("vehicle[]")[i],
            warehouse = warehouse,
            scale_quantity = scale_quantity
            )
            c.save()
            components.append(c)
            print(components)
            #update warehouse


            quantity = float(transaction_content.get("weight_brutto[]")[i].replace(',','.')) - float(transaction_content.get("weight_empty[]")[i].replace(',','.'))
            existing = False
            for slot in warehouse.slots.all():
                if item.pk == slot.item.pk:
                    if "plus" in tan_type:
                        slot.quantity += float(transaction_content.get("weight_brutto[]")[i].replace(',','.')) - float(
                            transaction_content.get("weight_empty[]")[i].replace(',','.'))
                    if "minus" in tan_type:
                        slot.quantity -= float(transaction_content.get("weight_brutto[]")[i].replace(',','.')) - float(
                            transaction_content.get("weight_empty[]")[i].replace(',','.'))
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
        transaction_type = tan_type,
        main_vehicle = transaction_content.get("main_vehicle_id")[0]
        )
        transaction.save()
        transaction.components.set(components)
        transaction.save()
        return redirect('/list/?sort=-pk')



    return render(request,'inventory/newentry.html', presets)

@csrf_exempt
def generate_delivery_note(request):
    transaction_pk = request.GET.get("tan", 1)
    transaction = Transaction.objects.get(pk=transaction_pk)
    components = transaction.components.all()


    with open(os.path.join(os.path.dirname(__file__), 'templates/lieferschein_template.html'), encoding='utf8') as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, features="html.parser")

    generation_date_field = soup.find(id="generation_date")
    generation_date_field.clear()
    generation_date_field.append(datetime.datetime.now().strftime("%d.%m.%Y, %H:%M"))

    tan_field = soup.find(id="transaction_id")
    tan_field.clear()
    tan_field.append(str(transaction_pk))

    c_types = {"company":"Agrarbetrieb", "private":"Privatperson"}
    customer = transaction.delivered_by
    customer_type_cont = c_types[customer.customer_type]
    customer_name_cont = "{} {}".format(customer.first_name, customer.name)
    customer_street_cont = customer.address.street
    customer_zip_cont = customer.address.plz
    customer_city_cont = customer.address.city
    customer_field = soup.find(id="delivered_by_id")
    customer_field.clear()
    customer_field.append(bs4.BeautifulSoup("{}<br>{}<br>{},<br>{} {}".format(
        customer_type_cont,
        customer_name_cont,
        customer_street_cont,
        customer_zip_cont,
        customer_city_cont
    ), features="html.parser", from_encoding="iso-8859-8"))

    types = {"plus":"Eingang", "minus":"Ausgang", "flux":"Umlagerung"}
    transaction_type_cont = transaction.transaction_type.__str__()
    transaction_type_field = soup.find(id="transaction_type")
    transaction_type_field.clear()
    transaction_type_field.append("{} vom: ".format(types[transaction_type_cont]))

    t = datetime.datetime.strptime("{} {}".format(transaction.date, transaction.time), "%Y-%m-%d %H:%M:%S")
    transaction_date_cont = t.strftime("%d.%m.%Y %H:%M")
    transaction_date_field = soup.find(id="transaction_date")
    transaction_date_field.clear()
    transaction_date_field.append("{}".format(transaction_date_cont))

    delivered_by_cont = "{} {}".format(customer.first_name, customer.name)
    delivered_by_field = soup.find(id="delivered_by")
    delivered_by_field.clear()
    delivered_by_field.append("{}".format(delivered_by_cont))

    done_by_cont = "Norbert Tendler"
    done_by_field = soup.find(id="done_by")
    done_by_field.clear()
    done_by_field.append("{}".format(done_by_cont))

    vehicle_id_cont = transaction.main_vehicle
    vehicle_id_field = soup.find(id="vehicle_id")
    vehicle_id_field.clear()
    vehicle_id_field.append("{}".format(vehicle_id_cont))

    transaction_table = soup.find(id="transaction_table")
    total_delivered = dict()
    for component in components:
        item = component.item.crop_name
        lager = component.warehouse.name
        feuchte = component.laboratory_analysis.feuchte
        fallzahl = component.laboratory_analysis.fallzahl
        ausputz = component.laboratory_analysis.ausputz
        mutterkorn = component.laboratory_analysis.feuchte
        kleinbruch = component.laboratory_analysis.kleinbruch
        hlgewicht = component.laboratory_analysis.hlgewicht
        fremdgetreide = component.laboratory_analysis.fremdgetreide
        auswuchs = component.laboratory_analysis.auswuchs
        date = "9"
        costs = "10"

        fahrzeug = component.scale_quantity.vehicle_id
        brutto_weight = component.scale_quantity.brutto_weight
        empty_weight = component.scale_quantity.empty_weight
        scale_id = component.scale_quantity.scale_number

        total_delivered[item] = total_delivered.get(item, 0) + float(brutto_weight) - float(empty_weight)

        row = '<tr style="border: 1px solid black;">' + \
              '        <td>{}</td>' + \
              '        <td>{}</td>' + \
              '     <td>' + \
              '         <table style="width: 90%">' + \
              '             <tr>' + \
              '                 <td>Feuchte </td>' + \
              '                 <td>{}</td>' + \
              '                 <td>Fallzahl </td>' + \
              '                 <td>{}</td>' + \
              '             </tr>' + \
              '             <tr>' + \
              '                 <td>Ausputz </td>' + \
              '                 <td>{}</td>' + \
              '                 <td>Mutterkorn </td>' + \
              '                 <td>{}</td>' + \
              '             </tr>' + \
              '             <tr>' + \
              '                  <td>Hl-Gewicht </td>' + \
              '                 <td>{}</td>' + \
              '                 <td>Fremdgetreide </td>' + \
              '                 <td>{}</td>' + \
              '             </tr>' + \
              '             <tr>' + \
              '                 <td>Auswuchs </td>' + \
              '                 <td>{}</td>' + \
              '                 <td>Kleinbruch </td>' + \
              '                <td>{}</td>' + \
              '             </tr>' + \
              '         </table>' + \
              '     </td>' + \
              '     <td>' + \
              '         <table style="width: 90%">' + \
              '             <tr>' + \
              '                 <td>Fahrzeug</td>' + \
              '                 <td>{}</td>' + \
              '            </tr>' + \
              '             <tr>' + \
              '                 <td>Brutto Gewicht</td>' + \
              '                 <td>{}</td>' + \
              '             </tr>' + \
              '             <tr>' + \
              '                 <td>Leergewicht</td>' + \
              '                 <td>{}</td>' + \
              '             </tr>' + \
              '             <tr>' + \
              '                 <td>Waage</td>' + \
              '                 <td>{}</td>' + \
              '             </tr>' + \
              '         </table>' + \
              '     </td>' + \
              ' </tr>'
        row = row.format(
            item,
            lager,
            feuchte,
            fallzahl,
            ausputz,
            mutterkorn,
            hlgewicht,
            fremdgetreide,
            auswuchs,
            kleinbruch,
            fahrzeug,
            brutto_weight,
            empty_weight,
            scale_id)
        transaction_table.append(bs4.BeautifulSoup(row, features="html.parser", from_encoding="iso-8859-8"))
    total_delivered_cont = ""
    for a in total_delivered.keys():
        total_delivered_cont += "{} {}kg ".format(a, total_delivered[a])
    total_delivered_field = soup.find(id="total_delivered")
    total_delivered_field.clear()
    total_delivered_field.append(total_delivered_cont)

    try:
        f_path = "./out.pdf"
        pdfkit.from_string(soup.__str__(), f_path, options={'encoding': 'utf-8'})
        with open(f_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/force_download")
            response['Content-Disposition'] = 'inline; filename=' + "Lieferschein_"+str(transaction_pk)+"_"+customer_name_cont+".pdf"
        return response
    except:
        with open("inventory/templates/out.html", "w+", encoding="utf8") as f:
            f.write(soup.__str__())
        return render(request,'out.html')


