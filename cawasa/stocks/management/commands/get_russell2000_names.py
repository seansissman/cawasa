from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, Index, IndexHistory
from bs4 import BeautifulSoup
from urllib2 import urlopen
import datetime
import contextlib
#

class Command(BaseCommand):
    help = 'Updates the list of names in the Russell 2000 index.'

    def handle(self, *args, **options):

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

        self.stdout.write("Wrote current Russell 2000 names to IndexHistory "
                          "for " + date.strftime("%m/%d/%Y") + ".")

        # for stock in stocks:
        #     symbol = stock[0].string
        #     name = stock[1].string
        #     try:
        #         sector = stock[2].string
        #         industry = stock[3].string
        #     except IndexError:
        #         sector = '?'
        #         industry = '?'
        #     print stock


# class Command(BaseCommand):
#     help = 'Updates the list of names in the S&P 500 index.'
#
#     def handle(self, *args, **options):
#
#         # Get (or create if doesn't exist) the Index object.
#         r2k_index_obj = self.get_or_create_r2k_index()
#
#         # URL of the data source
#         r2k_url = "http://www.barchart.com/stocks/russell2000.php?_dtp1=0"
#
#         # Today's date
#         date = datetime.date.today()
#
#         with contextlib.closing(urlopen(r2k_url)) as source_page:
#             # Create an html parser
#             soup = BeautifulSoup(source_page, 'html.parser')
#             # Find the table with our data
#             table = soup.find("table", {"class": "datatable ajax"})
#             if table:
#                 print "FOUND TABLE"
#             else:
#                 print "DID NOT FIND TABLE!!!"
#             # Fail now if we haven't found the right table
#             symbols = table.findAll('td', {"class": "ds_symbol"})
#             names = table.findall('td', {"class": "ds_name"})
#             print symbols

        #     header = table.findAll('th')
        #     if header[0].string != "Ticker symbol" or \
        #                                         header[1].string != "Security":
        #         raise Exception("Can't parse wikipedia's table!")
        #
        # # Retreive the values in the table
        # rows = table.findAll('tr')
        # for row in rows:
        #     fields = row.findAll('td')
        #     if fields:
        #         symbol = fields[0].string
        #         name = fields[1].string
        #         sector = fields[3].string
        #         industry = fields[4].string
        #         stock_obj, _ = Stock.objects.get_or_create(
        #                                                     name=name,
        #                                                     symbol=symbol,
        #                                                     sector=sector,
        #                                                     industry=industry)
        #
        #         # Creates the IndexHistory object if it doesn't exist
        #         IndexHistory.objects.get_or_create(date=date,
        #                                            index=sp_index_obj,
        #                                            stock=stock_obj)
        #
        # self.stdout.write("Wrote current S&P500 names to IndexHistory for " +
        #                   date.strftime("%m/%d/%Y") + ".")
    #

    def get_stock_obj(self, stocks, url):
        """ Returns a list of Stock objects. """
        stock_objs = []
        for stock in stocks[:5]:
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

