# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-04 01:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_auto_20160503_2117'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Names',
            new_name='Stock',
        ),
    ]
