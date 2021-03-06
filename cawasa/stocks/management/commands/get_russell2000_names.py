from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, Index, IndexHistory
from bs4 import BeautifulSoup
from urllib2 import urlopen
import datetime
import contextlib

class Command(BaseCommand):
    help = 'Updates the list of names in the Russell 2000 index.'

    def handle(self, *args, **options):
        if self.is_update_needed():     # R2k only rebalances once per year
            r2k_index_obj = self.get_or_create_r2k_index()
            r2k_url = "http://www.barchart.com/stocks/russell2000.php?_dtp1=0"
            stocks = self.get_r2k_names(r2k_url)

            gf_url = "https://www.google.com/finance?q=nyse:"
            stock_objs = self.get_stock_obj(stocks, gf_url)

            # Today's date
            date = datetime.date.today()

            for stock_obj in stock_objs:
                 IndexHistory.objects.get_or_create(date=date,
                                                    index=r2k_index_obj,
                                                    stock=stock_obj)

            self.stdout.write("Wrote current Russell 2000 names to "
                              "IndexHistory for " + date.strftime("%m/%d/%Y") +
                              ".")

    def is_update_needed(self):
        """ Returns True if database doesn't contain the
            latest reconstitution """
        try:
            latest = IndexHistory.objects.filter(
                index__symbol__iexact='.IUX').order_by('-date')[0]
        except IndexError:
            return True
        return latest.date.year < datetime.date.today().year


    def get_stock_obj(self, stocks, url):
        """ Returns a list of Stock objects. """
        stock_objs = []
        for stock in stocks:
            symbol = stock[0]
            name = stock[1]
            stock_obj = None
            try:
                stock_obj = Stock.objects.get(symbol__iexact=symbol,
                                              name__iexact=name)
            except Stock.DoesNotExist:
                sector, industry = '?', '?'
                with contextlib.closing(urlopen(url + symbol.lower())) \
                        as source_page:
                    soup = BeautifulSoup(source_page, 'html.parser')
                    divs = soup.find_all("div", {"class": "g-unit g-first"})
                    for d in divs:
                        if 'Sector:' in d.contents[0]:
                            links = d.find_all("a")
                            sector = links[0].contents[0]
                            industry = links[1].contents[0]
                stock.extend((sector, industry))
                stock_obj = Stock.objects.create(name=name,
                                                 symbol=symbol,
                                                 sector=sector,
                                                 industry=industry)
            except Stock.MultipleObjectsReturned:
                self.stdout.write('Multiple Stock objects found.  Check the '
                                  'database.')
                stock_obj = Stock.objects.filter(symbol__iexact=symbol,
                                                 name__iexact=name)[0]
            if stock_obj:
                stock_objs.append(stock_obj)
        return stock_objs

    def get_r2k_names(self, url):
        """ Returns list of [symbols, names]. """
        stocks = []
        with contextlib.closing(urlopen(url)) as source_page:
            # Create an html parser
            soup = BeautifulSoup(source_page, 'html.parser')
            # Find the table with our data
            table = soup.find("table", {"class": "datatable ajax"})
            if table:
                symbol_rows = table.find_all("td", {"class": "ds_symbol"})
                name_rows = table.find_all("td", {"class": "ds_name"})
                symbols = [s.a.contents[0] for s in symbol_rows]
                names = [n.a.contents[0] for n in name_rows]
                for s, n in zip(symbols, names):
                    stocks.append([s, n])
        return stocks

    def get_or_create_r2k_index(self):
        """ Returns Russell 2000 Index object. """
        obj, _ = Index.objects.get_or_create(
            name='Russell 2000',
            symbol='.IUX',
            description='The Russell 2000 Index is a small-cap stock market'
                        'index of the bottom 2,000 stocks in the Russell '
                        '3000 Index.'
            )
        return obj

