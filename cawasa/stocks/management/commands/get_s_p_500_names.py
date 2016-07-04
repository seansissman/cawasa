from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, Index, IndexHistory
from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import date
import contextlib
#import csv
#from os import mkdir
#from os.path import exists, join
#datadir = join('..', 'data')
#if not exists(datadir):
#    mkdir(datadir)

#source_page = open('List_of_S%26P_500_companies.html').read()

#source_page = urllib2.urlopen("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")

class Command(BaseCommand):
    help = 'Updates the list of names in the S&P 500 index.'

    def handle(self, *args, **options):

        sp_index_obj = self.get_or_create_sp_index()
        sp_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


        with contextlib.closing(urlopen(sp_url)) as source_page:

            soup = BeautifulSoup(source_page, 'html.parser')
            table = soup.find("table", { "class" : "wikitable sortable" })

            # Fail now if we haven't found the right table
            header = table.findAll('th')
            if header[0].string != "Ticker symbol" or header[1].string != "Security":
                raise Exception("Can't parse wikipedia's table!")

        # Retreive the values in the table
        records = []
        rows = table.findAll('tr')
        for row in rows:
            fields = row.findAll('td')
            if fields:
                symbol = fields[0].string
                name = fields[1].string
                sector = fields[3].string
                industry = fields[4].string

                stock_obj, stock_created = Stock.objects.get_or_create(name=name, symbol=symbol, sector=sector, industry=industry)
                stock_pk = stock_obj.pk

                IndexHistory.objects.get_or_create(date=date.today(), index=sp_index_obj, stock=stock_obj)

        self.stdout.write("Wrote S&P updates to DB.")

    def get_or_create_sp_index(self):
        """ Returns S&P 500 Index object. """
        obj, created = Index.objects.get_or_create(
            name='S&P 500',
            symbol='.INX',
            description='The Standard & Poor\'s 500, often abbreviated as the S&P 500, or just "the S&P", is an ' \
                        'American stock market index based on the market capitalizations of 500 large companies ' \
                        'having common stock listed on the NYSE or NASDAQ.'
            )
        return obj



        #obj.pk
                #records.append([symbol, name, sector, industry])
                # Stocks.objects.create(symbol=symbol, name=name, sector=sector,industry=industry, index='S&P 500')


#        header = ['Symbol', 'Name', 'Sector', 'Industry']
#        writer = csv.writer(open('../data/cawasa_constituents.csv', 'w'), lineterminator='\n')
#        writer.writerow(header)
#        # Sorting ensure easy tracking of modifications
#        records.sort(key=lambda s: s[1].lower())
#        writer.writerows(records)
