from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, Index, IndexHistory
from bs4 import BeautifulSoup
from urllib2 import urlopen
import datetime
import contextlib


class Command(BaseCommand):
    help = 'Updates the list of names in the S&P 500 index.'

    def handle(self, *args, **options):

        # Get (or create if doesn't exist) the Index object.
        sp_index_obj = self.get_or_create_sp_index()

        # URL of the data source
        sp_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

        # Today's date
        date = datetime.date.today()

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

                # Creates the IndexHistory object if it doesn't exist
                IndexHistory.objects.get_or_create(date=date,
                                                   index=sp_index_obj,
                                                   stock=stock_obj)

        self.stdout.write("Wrote current S&P500 names to IndexHistory for " +
                          date.strftime("%m/%d/%Y") + ".")

    def get_or_create_sp_index(self):
        """ Returns S&P 500 Index object. """
        obj, _ = Index.objects.get_or_create(
            name='S&P 500',
            symbol='.INX',
            description='The Standard & Poor\'s 500, often abbreviated as the'
                        ' S&P 500, or just "the S&P", is an American stock '
                        'market index based on the market capitalizations of '
                        '500 large companies having common stock listed '
                        'on the NYSE or NASDAQ.'
            )
        return obj

