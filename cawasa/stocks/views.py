from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import Http404
from django.template import loader
from django.views import generic
from django.views import generic
from .models import Stock, Index, IndexHistory
from .forms import SymbolLookup
#import difflib


def index(request):
    """ Return rendered all stocks orderd by symbol, stock lookup form,
        and any results from a stock lookup.
    """
    lookup_stocks = None
    if request.method == 'POST':  # If loaded from form (symbol lookup)
        form = SymbolLookup(request.POST)  # Form object with POST data
        if form.is_valid():
            symbol_lookup = form.cleaned_data['symbol_lookup']
            try:
                # Try to get an exact match on POST data
                exact_match = Stock.objects.get(symbol__iexact=symbol_lookup)
                return HttpResponseRedirect(exact_match.pk)
            except Stock.DoesNotExist:     # If no exact match
                lookup_stocks = Stock.objects.filter(symbol__icontains=
                                                     symbol_lookup).order_by(
                                                        'symbol')
                if not lookup_stocks:
                    lookup_stocks = '0'
    else:
        form = SymbolLookup()

    all_names = Stock.objects.order_by('symbol')
    ##template = loader.get_template('stocks/index.html')
    context = {'all_stocks_list': all_names, 'form': form, 'stock_lookup_list': lookup_stocks}
    return render(request, 'stocks/index.html', context)


def index_history(request, index_id):
    """ Returns rendered historical list of stocks within an index for
        index_id
    """
    ih = get_object_or_404(IndexHistory, pk=index_id)
    context = {'index_member_history': ih}
    return render(request, 'stocks/index_history.html', context)


class SummaryView(generic.DetailView):
    """ Generic View for the summary details of a stock """
    model = Stock
    template_name = 'stocks/summary.html'

#def summary(request, stock_id):
#    stock = get_object_or_404(Stock, pk=stock_id)
#    #try:
#    #    stock = Stock.objects.get(pk=stock_id)
#    #except Stock.DoesNotExist:
#    #    raise Http404("Stock is not currently in the DB.")
#    return render(request, 'stocks/summary.html', {'stock':stock})
#    #return HttpResponse("This will display the summary for stock with id = %s" % stock_id)


class IndexView(generic.ListView):
    """ Generic View for a listing of recorded indexes """
    model = Index
    template_name = 'stocks/indexes.html'


# class IndexHistoryView(generic.ListView):
#     model = IndexHistory
#     context_object_name = 'index_members_history'
#     template_name = 'stocks/index_hist# class IndexHistoryView(generic.ListView):
#     model = IndexHistory
#     context_object_name = 'index_members_history'
#     template_name = 'stocks/index_history.html'

    # def get_queryset(self):
    #     self.index = get_object_or_404(IndexHistory, pk=self.args[0])
    #     return IndexHistory.objects.filter(index=self.index)
    #
    # def get_context_data(self, **kwargs):
    #     context = super(IndexHistoryView, self).get_context_data(**kwargs)
    #     context['index'] = self.index
    #     return context


def index_names(request, index_id):
    return HttpResponse("This will return a list of names in index %s" % index_id)




#def symbol_lookup(request):
##    if request.method == 'POST':
#        form = SymbolLookup(request.POST)
#        if form.is_valid():
#            return HttpResponseRedirect('/thanks/')
#    else:
#        form = SymbolLookup()#

#    return render(request, 'stocks/index.html', {'form': form})
