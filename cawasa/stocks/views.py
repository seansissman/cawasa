from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import Http404
from django.template import loader
from .models import Stock


def index(request):
    #all_names = Stock.objects.values_list('symbol').order_by('symbol')
    all_names = Stock.objects.order_by('symbol')
    ##template = loader.get_template('stocks/index.html')
    context = {'all_stocks_list': all_names,}
    return render(request, 'stocks/index.html', context)
    ##return HttpResponse(template.render(context, request))
    #return HttpResponse("Hello, world. You're at the stocks index.")

def summary(request, stock_id):
    stock = get_object_or_404(Stock, pk=stock_id)
    #try:
    #    stock = Stock.objects.get(pk=stock_id)
    #except Stock.DoesNotExist:
    #    raise Http404("Stock is not currently in the DB.")
    return render(request, 'stocks/summary.html', {'stock':stock})
    #return HttpResponse("This will display the summary for stock with id = %s" % stock_id)

def index_names(request, index_id):
    return HttpResponse("This will return a list of names in index %s" % index_id)