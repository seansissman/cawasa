from __future__ import unicode_literals

from django.db import models


class Index(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=8)
    description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.symbol




class Stock(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=8)
    industry = models.CharField(max_length=30, blank=True)
    sector = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=500, blank=True)
    indexes = models.ManyToManyField(Index, blank=True)

    COMMON_STOCK = 'CS'
    EXCHANGE_TRADED_FUND = 'ETF'
    MUTUAL_FUND = 'MF'
    BOND = 'B'
    TYPE_CHOICES = (
        (COMMON_STOCK, 'Common Stock'),
        (EXCHANGE_TRADED_FUND, 'ETF'),
        (MUTUAL_FUND, 'Mutual Fund'),
        (BOND, 'Bond'),
    )
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, default=COMMON_STOCK)

    def __str__(self):
        return self.name



