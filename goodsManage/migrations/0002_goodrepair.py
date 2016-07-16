# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('goodsManage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodRepair',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('date', models.DateField(default=datetime.date.today, verbose_name='維修日期')),
                ('quantity', models.PositiveIntegerField(verbose_name='數量')),
                ('remark', models.TextField(blank=True, verbose_name='備註')),
                ('who', models.TextField(verbose_name='誰')),
                ('good', models.ForeignKey(to='goodsManage.Good')),
                ('person', models.ForeignKey(verbose_name='維修人', to='goodsManage.Person')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
