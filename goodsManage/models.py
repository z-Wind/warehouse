from django.db import models

# Create your models here.
from . import choices
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime
import re


class GoodKind(models.Model):
    code = models.CharField(verbose_name='代碼', max_length=10)
    name = models.CharField(verbose_name='種類', max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['code']


class Good(models.Model):
    type = models.CharField(verbose_name='型號', max_length=50)
    partNumber = models.CharField(blank=True, verbose_name='料號', max_length=13)
    partNumber_once = models.CharField(blank=True, verbose_name='一次性料號',
                                       max_length=13)
    partNumber_old = models.CharField(blank=True, verbose_name='舊料號',
                                      max_length=13)
    description = models.TextField(blank=True)
    kind = models.ForeignKey(GoodKind)
    thumbnail = models.ImageField(verbose_name='縮圖', upload_to='goods', blank=True, null=True)

    def __str__(self):
        return self.type

    def clean(self):
        if re.search(r'[,"\']', self.type):
            raise ValidationError('命名不能有特殊字元 , " \' ')

    class Meta:
        ordering = ['type']


class Department(models.Model):
    code = models.CharField(verbose_name='代碼', max_length=10)
    name = models.CharField(verbose_name='名稱', max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['code']


class Person(models.Model):
    name = models.CharField(verbose_name='姓名', max_length=6)
    department = models.ForeignKey(Department)

    def __str__(self):
        return self.department.name + " : " + self.name

    class Meta:
        ordering = ['department']


class GoodRequisition(models.Model):
    # 在 `ForeignKey` 的狀況中，
    # Django 預設會用 model 的名稱後面加 `_set` 來當作 reverse relation 的名稱，
    # 所以 `GoodRequisition.good` 的預設
    # reverse relation key 會是 `Good.goodrequisition_set` 全小寫。
    good = models.ForeignKey(Good, related_name='goodrequisition_set')
    person = models.ForeignKey(Person, verbose_name='領用人')
    datetime = models.DateTimeField(default=timezone.now, verbose_name='領用日期')
    quantity = models.PositiveIntegerField(verbose_name='數量')
    remark = models.TextField(blank=True, verbose_name='備註')
    who = models.TextField(verbose_name='誰')

    def __str__(self):
        return self.good.type

    class Meta:
        ordering = ['-datetime']


class GoodBack(models.Model):
    good = models.ForeignKey(Good)
    person = models.ForeignKey(Person, verbose_name='歸還人')
    datetime = models.DateTimeField(default=timezone.now, verbose_name='歸還日期')
    quantity = models.PositiveIntegerField(verbose_name='數量')
    remark = models.TextField(blank=True, verbose_name='備註')
    who = models.TextField(verbose_name='誰')

    def __str__(self):
        return self.good.type

    class Meta:
        ordering = ['-datetime']


class GoodInventory(models.Model):
    good = models.ForeignKey(Good)
    department = models.ForeignKey(Department, verbose_name='部門')
    quantity = models.PositiveIntegerField(verbose_name='數量')
    remark = models.TextField(blank=True, verbose_name='備註')
    who = models.TextField(verbose_name='誰')

    def __str__(self):
        return self.good.type

    class Meta:
        ordering = ['good__type', 'department']


class GoodBuy(models.Model):
    good = models.ForeignKey(Good)
    person = models.ForeignKey(Person, verbose_name='購買人')
    date = models.DateField(default=datetime.date.today, verbose_name='入料日期')
    quantity = models.PositiveIntegerField(verbose_name='數量')
    pr = models.CharField(verbose_name='PR', max_length=12)
    po = models.CharField(verbose_name='PO', max_length=11)
    remark = models.TextField(blank=True, verbose_name='備註')
    who = models.TextField(verbose_name='誰')

    def __str__(self):
        return self.good.type

    class Meta:
        ordering = ['-date']


class GoodAllocate(models.Model):
    good = models.ForeignKey(Good)
    person = models.ForeignKey(Person, verbose_name='調出人')
    toDepartment = models.ForeignKey(Department, verbose_name='調入部門')
    datetime = models.DateTimeField(default=timezone.now, verbose_name='調撥日期')
    quantity = models.PositiveIntegerField(verbose_name='數量')
    remark = models.TextField(verbose_name='備註')
    who = models.TextField(verbose_name='誰')

    def __str__(self):
        return self.good.type

    class Meta:
        ordering = ['-datetime']


class WastageStatus(models.Model):
    code = models.CharField(verbose_name='代碼', max_length=10)
    name = models.CharField(verbose_name='狀態', max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['code']


class GoodWastage(models.Model):
    good = models.ForeignKey(Good)
    person = models.ForeignKey(Person, verbose_name='耗損人')
    datetime = models.DateTimeField(default=timezone.now, verbose_name='耗損日期')
    quantity = models.PositiveIntegerField(verbose_name='數量')
    status = models.ForeignKey(WastageStatus)
    remark = models.TextField(blank=True, verbose_name='備註')
    who = models.TextField(verbose_name='誰')

    def __str__(self):
        return self.good.type

    class Meta:
        ordering = ['-datetime']


class GoodRepair(models.Model):
    good = models.ForeignKey(Good)
    person = models.ForeignKey(Person, verbose_name='維修人')
    date = models.DateField(default=datetime.date.today, verbose_name='維修日期')
    quantity = models.PositiveIntegerField(verbose_name='數量')
    remark = models.TextField(blank=True, verbose_name='備註')
    who = models.TextField(verbose_name='誰')

    def __str__(self):
        return self.good.type

    class Meta:
        ordering = ['-date']
