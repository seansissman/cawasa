from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, Index, IndexHistory
from bs4 import BeautifulSoup
from urllib2 import urlopen
import datetime
import contextlib


class Command(BaseCommand):
    help = 'Updates the database or the provided argument.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('arguments', nargs='+', type=str)

    def handle(self, *args, **options):

        # Set index and stock names per arg
        for each in options['arguments']:
            pass
            a = each.upper()
            if any(a == opt for opt in ('SP500', 'SandP500', 'SP', 'SandP'
                                        '.INX', 'INX')):
                print "Process SP500"
                if self.is_update_needed('.INX'):
                    index_obj = self.get_or_create_index('sp500')
                    stock_objs = self.get_sp500_objects()
            elif any(a == opt for opt in ('RUSSELL2000', 'RUSSELL2K', 'R2K',
                                          'RUS2K', 'RUS2000', '.IUX', 'IUX')):
                print "Processing R2k"
                if self.is_update_needed('.IUX'):
                    index_obj = self.get_or_create_index('r2k')
                    stock_objs = self.get_r2k_objects()

            else:
                self.stderr.write('Invalid Argument!!!')

            # self.update_index_history(datetime.date.today(), index_obj,
            #                           stock_objs)

    def get_sp500_objects(self):
        """ Returns a list of Stock objects for current S&P 500"""
        sp500_objs = []
        # URL of the data source
        sp_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

        with contextlib.closing(urlopen(sp_url)) as source_page:
            # Create an html parser
            soup = BeautifulSoup(source_page, 'html.parser')
            # Find the table with our data
            table = soup.find("table", {"class": "wikitable sortable"})
            # Fail now if we haven't found the right table
            header = table.findAll('th')
            if header[0].string != "Ticker symbol" or \
                                    header[1].string != "Security":
                raise Exception("Can't parse wikipedia's table!")

        # Retreive the values in the table
        rows = table.findAll('tr')
        for row in rows:
            fields = row.findAll('td')
            if fields:
                symbol = fields[0].string
                name = fields[1].string
                sector = fields[3].string
                industry = fields[4].string
                stock_obj, _ = Stock.objects.get_or_create(
                                                            name=name,
                                                            symbol=symbol,
                                                            sector=sector,
                                                            industry=industry)
                sp500_objs.append(stock_obj)
        return sp500_objs

    def get_r2k_objects(self):
        """ Returns a list of Stock object for he current Russell 2000 """
        r2k_objs = []
        r2k_url = "http://www.barchart.com/stocks/russell2000.php?_dtp1=0"
        stocks = []
        self.stdout.write('Searching for Russell 2000 stocks.')
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
        self.stdout.write('Found {} stocks in R2k.'.format(len(stocks)))
        self.stdout.write('Getting or creating Stock objects...')
        gf_url = "https://www.google.com/finance?q=nyse:"
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
                r2k_objs.append(stock_obj)
        self.stdout.write('Returning {} Stock objects.'.format(len(r2k_objs)))
        return r2k_objs

    def update_index_history(self, date, index_obj, stock_objs):
        # Creates the IndexHistory object if it doesn't exist
        for stock_obj in stock_objs:
            IndexHistory.objects.get_or_create(date=date,
                                               index=index_obj,
                                               stock=stock_obj)

        self.stdout.write("Wrote current S&P500 names to IndexHistory for " +
                          date.strftime("%m/%d/%Y") + ".")

    def get_or_create_index(self, index):
        """ Returns the Index object. """
        name, symbol, description = '', '', ''
        if index == 'sp500':
            name = 'S&P 500'
            symbol = '.INX'
            description = 'The Standard & Poor\'s 500, often abbreviated as '\
                          'the S&P 500, or just "the S&P", is an American '\
                          'stock market index based on the market '\
                          'capitalizations of 500 large companies having '\
                          'common stock listed on the NYSE or NASDAQ.'

        elif index == 'r2k':
            name = 'Russell 2000'
            symbol = '.IUX'
            description = 'The Russell 2000 Index is a small-cap stock market'\
                          'index of the bottom 2,000 stocks in the Russell '\
                          '3000 Index.'
        if name and symbol and description:
            obj, _ = Index.objects.get_or_create(
                name=name,
                symbol=symbol,
                description=description)
            return obj
        else:
            self.stderr.write('No valid index.')

    def is_update_needed(self, index_symbol):
        """ Returns True if database doesn't contain the
            latest reconstitution """
        try:
            latest = IndexHistory.objects.filter(
                index__symbol__iexact=index_symbol).order_by('-date')[0]
        except IndexError:
            return True
        if index_symbol == '.INX':
            return latest.date == datetime.date.today()
        if index_symbol == '.IUX':
            return latest.date.year < datetime.date.today().year

