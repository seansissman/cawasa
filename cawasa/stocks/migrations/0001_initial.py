# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-29 02:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Indexes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('symbol', models.CharField(max_length=8)),
                ('description', models.CharField(blank=True, max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Names',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('symbol', models.CharField(max_length=8)),
                ('industry', models.CharField(blank=True, max_length=30)),
                ('sector', models.CharField(blank=True, max_length=30)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('type', models.CharField(choices=[('CS', 'Common Stock'), ('ETF', 'ETF'), ('MF', 'Mutual Fund'), ('B', 'Bond')], default='CS', max_length=3)),
                ('indexes', models.ManyToManyField(blank=True, to='stocks.Indexes')),
            ],
        ),
    ]
