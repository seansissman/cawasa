from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, Index, IndexHistory
import quandl

class Command(BaseCommand):

    quandl.ApiConfig.api_key = 'puK-R-gM-ELyjbQx5KMA'

    def handle(self, *args, **options):
        self.get_index_symbols('.INX')

    def get_index_symbols(self, index):
        """ Returns a generator of the symbols for the provided index """
        i = Index.objects.get(symbol__iexact=index)
        latest_date = IndexHistory.objects.filter(index=i).latest('date').date
        s = IndexHistory.objects.filter(index=i).filter(date=latest_date)
        symbols = (each.stock.symbol for each in s)
        return symbols

    # data = quandl.get("WIKI/FB")
    #
    # print data.columns
    # print data.loc[data.index[0]]
    # for each in data.index:
    #     print each
