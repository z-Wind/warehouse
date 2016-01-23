# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(verbose_name='代碼', max_length=10)),
                ('name', models.CharField(verbose_name='名稱', max_length=10)),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Good',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(verbose_name='型號', max_length=50)),
                ('partNumber', models.CharField(max_length=13, verbose_name='料號', blank=True)),
                ('partNumber_once', models.CharField(max_length=13, verbose_name='一次性料號', blank=True)),
                ('partNumber_old', models.CharField(max_length=13, verbose_name='舊料號', blank=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['type'],
            },
        ),
        migrations.CreateModel(
            name='GoodAllocate',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='調撥日期')),
                ('quantity', models.PositiveIntegerField(verbose_name='數量')),
                ('remark', models.TextField(verbose_name='備註')),
                ('who', models.TextField(verbose_name='誰')),
                ('good', models.ForeignKey(to='goodsManage.Good')),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='GoodBack',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='歸還日期')),
                ('quantity', models.PositiveIntegerField(verbose_name='數量')),
                ('remark', models.TextField(verbose_name='備註', blank=True)),
                ('who', models.TextField(verbose_name='誰')),
                ('good', models.ForeignKey(to='goodsManage.Good')),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='GoodBuy',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='入料日期')),
                ('quantity', models.PositiveIntegerField(verbose_name='數量')),
                ('pr', models.CharField(verbose_name='PR', max_length=12)),
                ('po', models.CharField(verbose_name='PO', max_length=11)),
                ('remark', models.TextField(verbose_name='備註', blank=True)),
                ('who', models.TextField(verbose_name='誰')),
                ('good', models.ForeignKey(to='goodsManage.Good')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='GoodInventory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='數量')),
                ('remark', models.TextField(verbose_name='備註', blank=True)),
                ('who', models.TextField(verbose_name='誰')),
                ('department', models.ForeignKey(verbose_name='部門', to='goodsManage.Department')),
                ('good', models.ForeignKey(to='goodsManage.Good')),
            ],
            options={
                'ordering': ['good__type', 'department'],
            },
        ),
        migrations.CreateModel(
            name='GoodKind',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(verbose_name='代碼', max_length=10)),
                ('name', models.CharField(verbose_name='種類', max_length=10)),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='GoodRequisition',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='領用日期')),
                ('quantity', models.PositiveIntegerField(verbose_name='數量')),
                ('remark', models.TextField(verbose_name='備註', blank=True)),
                ('who', models.TextField(verbose_name='誰')),
                ('good', models.ForeignKey(related_name='goodrequisition_set', to='goodsManage.Good')),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='GoodWastage',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='耗損日期')),
                ('quantity', models.PositiveIntegerField(verbose_name='數量')),
                ('remark', models.TextField(verbose_name='備註', blank=True)),
                ('who', models.TextField(verbose_name='誰')),
                ('good', models.ForeignKey(to='goodsManage.Good')),
            ],
            options={
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(verbose_name='姓名', max_length=6)),
                ('department', models.ForeignKey(to='goodsManage.Department')),
            ],
            options={
                'ordering': ['department'],
            },
        ),
        migrations.CreateModel(
            name='WastageStatus',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(verbose_name='代碼', max_length=10)),
                ('name', models.CharField(verbose_name='狀態', max_length=10)),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.AddField(
            model_name='goodwastage',
            name='person',
            field=models.ForeignKey(verbose_name='耗損人', to='goodsManage.Person'),
        ),
        migrations.AddField(
            model_name='goodwastage',
            name='status',
            field=models.ForeignKey(to='goodsManage.WastageStatus'),
        ),
        migrations.AddField(
            model_name='goodrequisition',
            name='person',
            field=models.ForeignKey(verbose_name='領用人', to='goodsManage.Person'),
        ),
        migrations.AddField(
            model_name='goodbuy',
            name='person',
            field=models.ForeignKey(verbose_name='購買人', to='goodsManage.Person'),
        ),
        migrations.AddField(
            model_name='goodback',
            name='person',
            field=models.ForeignKey(verbose_name='歸還人', to='goodsManage.Person'),
        ),
        migrations.AddField(
            model_name='goodallocate',
            name='person',
            field=models.ForeignKey(verbose_name='調出人', to='goodsManage.Person'),
        ),
        migrations.AddField(
            model_name='goodallocate',
            name='toDepartment',
            field=models.ForeignKey(verbose_name='調入部門', to='goodsManage.Department'),
        ),
        migrations.AddField(
            model_name='good',
            name='kind',
            field=models.ForeignKey(to='goodsManage.GoodKind'),
        ),
    ]
