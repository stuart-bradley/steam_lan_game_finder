# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-15 06:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('appid', models.IntegerField(editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('is_multiplayer', models.BooleanField(default=False)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('is_multiplayer', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='tags',
            field=models.ManyToManyField(to='game_finder.Tag'),
        ),
    ]
