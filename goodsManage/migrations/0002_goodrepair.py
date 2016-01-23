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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('date', models.DateField(verbose_name='維修日期', default=datetime.date.today)),
                ('quantity', models.PositiveIntegerField(verbose_name='數量')),
                ('remark', models.TextField(verbose_name='備註', blank=True)),
                ('who', models.TextField(verbose_name='誰')),
                ('good', models.ForeignKey(to='goodsManage.Good')),
                ('person', models.ForeignKey(to='goodsManage.Person', verbose_name='維修人')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
