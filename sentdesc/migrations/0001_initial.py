# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-08 18:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Atributos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atributo', models.CharField(max_length=200)),
                ('tipo', models.CharField(max_length=20)),
                ('detalhamento', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Atributos_Habilidades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.TextField()),
                ('atributo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sentdesc.Atributos')),
            ],
        ),
        migrations.CreateModel(
            name='Habilidades_Leitura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_origem', models.IntegerField(default=0)),
                ('origem', models.CharField(max_length=200)),
                ('sent_desc', models.TextField(verbose_name='Sentença Descritora')),
            ],
        ),
        migrations.AddField(
            model_name='atributos_habilidades',
            name='habilidades',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sentdesc.Habilidades_Leitura'),
        ),
    ]
