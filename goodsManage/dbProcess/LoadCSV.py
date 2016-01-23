#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Load Data From csv"""

__author__ = "子風"
__copyright__ = "Copyright 2015, Sun All rights reserved"
__version__ = "1.0.0"

import csv
from goodsManage.models import *
from goodsManage import choices
import datetime
import pytz
import tkinter as tk
from tkinter import filedialog

def findkey(dic, value):
    key = None
    for k in dic:
        if dic[k] == value:
            key = k
            break
            
    return key

def stripAll(str):
    str = str.replace('\n',' ')
    str = str.replace('\r',' ')
    str = str.strip()
    
    return str

def init():
    
    bulklist = []
    for temp in choices.DEPARTMENT_CHOICES:
        try:
            Department.objects.get(code = temp[0], name = temp[1])
        except Department.DoesNotExist:
            bulklist.append(Department(code = temp[0], name = temp[1]))
        except Department.MultipleObjectsReturned:
            print('重覆 => ', temp[0] + " : " + temp[1])
            print('----------------------')
            continue
    if bulklist:
        Department.objects.bulk_create(bulklist)
            
    bulklist = []
    for temp in choices.KIND_CHOICES:
        try:
            GoodKind.objects.get(code = temp[0], name = temp[1])
        except GoodKind.DoesNotExist:
            bulklist.append(GoodKind(code = temp[0], name = temp[1]))
        except GoodKind.MultipleObjectsReturned:
            print('重覆 => ', temp[0] + " : " + temp[1])
            print('----------------------')
            continue
    if bulklist:
        GoodKind.objects.bulk_create(bulklist)
        
    bulklist = []
    for temp in choices.WASTAGE_STATUS_CHOICES:
        try:
            WastageStatus.objects.get(code = temp[0], name = temp[1])
        except WastageStatus.DoesNotExist:
            bulklist.append(WastageStatus(code = temp[0], name = temp[1]))
        except WastageStatus.MultipleObjectsReturned:
            print('重覆 => ', temp[0] + " : " + temp[1])
            print('----------------------')
            continue
    if bulklist:
        WastageStatus.objects.bulk_create(bulklist)
        
    
def csvToGood(filepath):
    line = 0
    GoodList = []
    with open(filepath, 'r', newline='') as csvfile:
        for row in csv.DictReader(csvfile, ["新料號", "一次性料號", "舊料號", "型號", "敘述", "種類"]):
            partNumber = stripAll(row['新料號'])
            partNumber_once = stripAll(row['一次性料號'])
            partNumber_old = stripAll(row['舊料號'])
            type = stripAll(row['型號'])
            description = row['敘述'] if row['敘述'] else ''
            
            # 忽略第一行
            if line == 0:
                line += 1
                continue
            
            temp = stripAll(row['種類'])
            try:    
                kind, created = GoodKind.objects.get_or_create(name = temp)
            except GoodKind.DoesNotExist:
                print('種類不存在 => ', temp)
                print('----------------------')
                continue
            except GoodKind.MultipleObjectsReturned:
                print('種類重覆 => ', temp)
                print('----------------------')
                continue
            
            try:
                if list(filter(lambda x: x.type == type, GoodList)):
                    print('重覆 => ', type)
                    print('----------------------')
                    continue
                    
                good = Good.objects.get(type = type)
            except Good.MultipleObjectsReturned:
                print('重覆 => ', type)
                print('----------------------')
                continue
            except Good.DoesNotExist:
                GoodList.append(Good(type=type, partNumber=partNumber, partNumber_once=partNumber_once, partNumber_old=partNumber_old, description=description, kind=kind))
            else:
                print('已有 => ', type)
                print('----------------------')
                continue
    
    if GoodList:
        Good.objects.bulk_create(GoodList)
            
            
def csvToGoodInventory(filepath):
    line = 0
    itemlist = ["種類", "型號", "料號", "部門", "庫存量", "進貨量"]
    GoodInventoryList = []
    with open(filepath, 'r', newline='') as csvfile:
        for row in csv.DictReader(csvfile, itemlist):
            type = stripAll(row['型號'])
                
            # 忽略第一行
            if line == 0:
                line += 1
                continue
                
            try:    
                good = Good.objects.get(type = type)
            except Good.DoesNotExist:
                print('不存在 => ', type)
                print('----------------------')
                continue
            except Good.MultipleObjectsReturned:
                print('重覆 => ', type)
                print('----------------------')
                continue
            
            dname = stripAll(row['部門'])
            try:    
                department = Department.objects.get(name = dname)
            except Department.DoesNotExist:
                print('部門不存在 => ', dname)
                print('----------------------')
                continue
            except Department.MultipleObjectsReturned:
                print('部門重覆 => ', dname)
                print('----------------------')
                continue
            
            
            quantity = int(stripAll(row['庫存量']))
            remark = row.get('備註', '')
            who = 'csv'
            
            try:
                goodInventory = GoodInventory.objects.get(good = good, department = department)
            except GoodInventory.MultipleObjectsReturned:
                print('{0} 重覆 => {1} => '.format(department, type))
                print('----------------------')
                continue
            except GoodInventory.DoesNotExist:
                GoodInventoryList.append(GoodInventory(good=good, department=department, quantity=quantity, remark=remark, who=who))
                #GoodInventory.objects.create(good=good, department=department, quantity=quantity, remark=remark, who=who)
                continue
            else:
                if goodInventory.quantity < quantity:
                    print('{0} {1} 更新數量 {2} => {3} '.format(department, type,  goodInventory.quantity, quantity))
                    print('----------------------')
                    goodInventory.quantity = quantity
                    goodInventory.save()
                #else:
                #    print('{0} 已有 => {1}'.format(department, type))
                #    print('----------------------')
                continue
    
    if GoodInventoryList:
        GoodInventory.objects.bulk_create(GoodInventoryList)
    
    
def csvToGoodRequisition(filepath):
    line = 0
    itemlist = ["種類", "型號", "料號", "部門", "領用人", "領用日期",  "領用量", "備註"]
    dateformat = "%Y-%m-%d %H:%M"
    GoodRequisitionList = []
    with open(filepath, 'r', newline='') as csvfile:
        for row in csv.DictReader(csvfile, itemlist):
            type = stripAll(row['型號'])

            # 忽略第一行
            if line == 0:
                line += 1
                continue

            try:
                good = Good.objects.get(type = type)
            except Good.DoesNotExist:
                print('不存在 => ', type)
                print('----------------------')
                continue
            except Good.MultipleObjectsReturned:
                print('重覆 => ', type)
                print('----------------------')
                continue

            temp = stripAll(row['部門'])
            try:    
                department = Department.objects.get(name = temp)
            except Department.DoesNotExist:
                print('部門不存在 => ', temp)
                print('----------------------')
                continue
            except Department.MultipleObjectsReturned:
                print('部門重覆 => ', temp)
                print('----------------------')
                continue
                
            temp = stripAll(row['領用人'])
            try:    
                person, created = Person.objects.get_or_create(name = temp, department = department)
            except Person.MultipleObjectsReturned:
                print('人名重覆 => ', temp)
                print('----------------------')
                continue
                
            
            tz = pytz.timezone('Asia/Taipei')
            datetimeEx = tz.localize(datetime.datetime.strptime(stripAll(row['領用日期'])[:16], dateformat))
            quantity = int(stripAll(row['領用量']))
            remark = row['備註'] if row['備註'] else ''
            who = 'csv'
            
            if quantity > 0:
                # GoodRequisition.objects.create(locals())
                GoodRequisitionList.append(GoodRequisition(good=good, person=person, datetime=datetimeEx, quantity=quantity, remark=remark, who=who))
    
    if GoodRequisitionList:
        GoodRequisition.objects.bulk_create(GoodRequisitionList)

def csvToGoodRequisitionInitial(filepath):
    line = 0
    GoodRequisitionList = []

    with open(filepath, 'r', newline='') as csvfile:
        for line, row in enumerate(csv.reader(csvfile)):
            # 忽略第一行第二行
            if line <= 1:
                continue
            elif line == 2:
                typeList = [stripAll(type) for type in row[2:]]
            else:
                for col, data in enumerate(row):     
                    if col == 0:
                        if stripAll(data):
                            dname = stripAll(data)
                            try:    
                                department = Department.objects.get(name = dname)
                            except Department.DoesNotExist:
                                print('部門不存在 => ', dname)
                                print('----------------------')
                                continue
                            except Department.MultipleObjectsReturned:
                                print('部門重覆 => ', dname)
                                print('----------------------')
                                continue
                        else:
                            break
                    elif col == 1:
                        temp = stripAll(data)
                        try:    
                            person, created = Person.objects.get_or_create(name = temp, department = department)
                        except Person.MultipleObjectsReturned:
                            print('人名重覆 => ', temp)
                            print('----------------------')
                            continue
                    else:
                        type = typeList[col-2]
                        try:
                            good = Good.objects.get(type = type)
                        except Good.DoesNotExist:
                            print('不存在 => ', type)
                            print('----------------------')
                            continue
                        except Good.MultipleObjectsReturned:
                            print('重覆 => ', type)
                            print('----------------------')
                            continue
                        
                        if data.upper() == 'V':
                            tz = pytz.timezone('Asia/Taipei')
                            datetimeEx = tz.localize(datetime.datetime.now())
                            quantity = 1
                            remark = '初始化'
                            who = 'csv'
                            
                            # GoodRequisition.objects.create(locals())
                            GoodRequisitionList.append(GoodRequisition(good=good, person=person, datetime=datetimeEx, quantity=quantity, remark=remark, who=who))
    
    if GoodRequisitionList:
        GoodRequisition.objects.bulk_create(GoodRequisitionList)

        
def main():
    init()

    root = tk.Tk()
    root.withdraw()
    filePath = tk.filedialog.askopenfilename(filetypes=(("Good File", "*.csv"),
                                           ("All files", "*.*") ))
    if filePath:
        csvToGood(filePath)
    
    filePath = tk.filedialog.askopenfilename(filetypes=(("GoodInventory File", "*.csv"),
                                           ("All files", "*.*") ))
    if filePath:
        csvToGoodInventory(filePath)
        
    filePath = tk.filedialog.askopenfilename(filetypes=(("GoodRequisition File", "*.csv"),
                                           ("All files", "*.*") ))
    if filePath:
        csvToGoodRequisition(filePath)
        
    filePath = tk.filedialog.askopenfilename(filetypes=(("GoodRequisitionInitial File", "*.csv"),
                                           ("All files", "*.*") ))
    if filePath:
        csvToGoodRequisitionInitial(filePath)

if __name__ == '__main__':
    main()
    

