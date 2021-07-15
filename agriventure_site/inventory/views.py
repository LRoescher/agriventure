from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from .models import Transaction

def index(request):
    try:
        template = loader.get_template('inventory/index.html')
    except:
        raise Http404("Error occured!")

    return HttpResponse(template.render())

def newentry(request):
    try:
        template = loader.get_template('inventory/newentry.html')
    except:
        raise Http404("Error occured!")

    return HttpResponse(template.render())

def list(request):
    try:
        objs = Transaction.objects.all()
    except:
        raise Http404("Error occured!")

    return render(request,'inventory/list.html',{'objs':objs})

