# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-21 11:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sentdesc', '0002_auto_20170214_1612'),
    ]

    operations = [
        migrations.CreateModel(
            name='Elementos_Texto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.IntegerField(default=0)),
                ('elemento', models.CharField(max_length=200, unique=True, verbose_name='Elementos do Texto')),
            ],
        ),
        migrations.AlterField(
            model_name='atributos',
            name='tipo',
            field=models.CharField(choices=[('TXT', 'Texto'), ('NBR', 'Número'), ('LTXT', 'Texto Grande'), ('DT', 'Data'), ('TAB', 'Tabela Externa')], default='TXT', max_length=4),
        ),
    ]