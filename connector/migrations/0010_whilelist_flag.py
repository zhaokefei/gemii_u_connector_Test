# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-22 14:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0009_whilelist'),
    ]

    operations = [
        migrations.AddField(
            model_name='whilelist',
            name='flag',
            field=models.CharField(default=1, max_length=10, verbose_name='\u72b6\u6001'),
        ),
    ]