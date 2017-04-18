# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-09 21:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_auto_20170306_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='location',
            field=models.CharField(default='Durham', max_length=200),
        ),
        migrations.AddField(
            model_name='message',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]