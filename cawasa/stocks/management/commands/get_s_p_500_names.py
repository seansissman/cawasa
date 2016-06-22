from django.core.management.base import BaseCommand, CommandError
from stocks.models import Stock, Index
from bs4 import BeautifulSoup
from urllib2 import urlopen
import contextlib
import csv
from os import mkdir
from os.path import exists, join
datadir = join('..', 'data')
if not exists(datadir):
    mkdir(datadir)

#source_page = open('List_of_S%26P_500_companies.html').read()

#source_page = urllib2.urlopen("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")

class Command(BaseCommand):
    help = 'Updates the list of names in the S&P 500 index.'

    def handle(self, *args, **options):
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

                obj, created = Stock.objects.get_or_create(name=name, symbol=symbol, sector=sector, industry=industry)
        self.stdout.write("Wrote S&P updated to DB.")
                #obj.pk
                #records.append([symbol, name, sector, industry])
                # Stocks.objects.create(symbol=symbol, name=name, sector=sector,industry=industry, index='S&P 500')


#        header = ['Symbol', 'Name', 'Sector', 'Industry']
#        writer = csv.writer(open('../data/cawasa_constituents.csv', 'w'), lineterminator='\n')
#        writer.writerow(header)
#        # Sorting ensure easy tracking of modifications
#        records.sort(key=lambda s: s[1].lower())
#        writer.writerows(records)
