# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-06 15:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='food',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='user',
            name='food_listed',
        ),
        migrations.RemoveField(
            model_name='user',
            name='location',
        ),
        migrations.AddField(
            model_name='food',
            name='date_listed',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='food',
            name='user',
            field=models.ForeignKey(default='root', on_delete=django.db.models.deletion.CASCADE, to='backend.User'),
        ),
    ]
