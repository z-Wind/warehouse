# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import redirect

# modules from django
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.six.moves import range
from django.http import StreamingHttpResponse
from django.db.models import Q, Sum

# Create your views here.
import datetime
import pytz
import csv
import socket

from .models import *
from .forms import *
from . import choices

#global variable
alldatas = {'name':None, 'data':[]}

# page
def page_setting(objs, pageNum, dataNum = 50):
    # Show n contacts per page
    paginator = Paginator(objs, per_page = dataNum)

    try:
        page = paginator.page(pageNum)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        if int(pageNum) > paginator.num_pages:
            page = paginator.page(1)
        else:
            page = paginator.page(paginator.num_pages)

    return page


# inquiry and filter
def objsInquiryFilter(objs, inquiry, afterShow = False):
    fnameList = objs.model._meta.get_all_field_names()
    # 尋找分類
    if inquiry.is_valid():
        type = inquiry.cleaned_data['type'].strip()
        if type: # contain str
            if objs.model is Good:
                objs = objs.filter(type__icontains = type)
            elif 'good' in fnameList:
                objs = objs.filter(good__type__icontains = type)

        partNumber = inquiry.cleaned_data['partNumber'].strip()
        if partNumber:
            if objs.model is Good:
                objs = objs.filter(Q(partNumber__icontains = partNumber) \
                                 | Q(partNumber_once__icontains = partNumber) \
                                 | Q(partNumber_old__icontains = partNumber))
            elif 'good' in fnameList:
                objs = objs.filter(Q(good__partNumber__icontains = partNumber) \
                                 | Q(good__partNumber_once__icontains = partNumber) \
                                 | Q(good__partNumber_old__icontains = partNumber))

        kinds = inquiry.cleaned_data['kind']
        if kinds:
            if objs.model is GoodKind:
                objs = objs.filter(code__in = kinds)
            elif objs.model is Good:
                objs = objs.filter(kind__code__in = kinds)
            elif 'good' in fnameList:
                objs = objs.filter(good__kind__code__in = kinds)

        departments = inquiry.cleaned_data['department']
        if departments and 'All' not in departments:
            if objs.model is Department:
                objs = objs.filter(code__in = departments)
            elif 'department' in fnameList:
                objs = objs.filter(department__code__in = departments)
            elif 'person' in objs.model._meta.get_all_field_names():
                objs = objs.filter(person__department__code__in = departments)

        toDepartments = inquiry.cleaned_data['toDepartment']
        if toDepartments and 'All' not in toDepartments:
            if objs.model is Department:
                objs = objs.filter(code__in = toDepartments)
            elif 'toDepartment' in fnameList:
                objs = objs.filter(toDepartment__code__in = toDepartments)

        fromDate = inquiry.cleaned_data['fromDate']
        toDate = inquiry.cleaned_data['toDate']
        if fromDate and toDate:
            if 'date' in fnameList:
                min_dt = fromDate
                max_dt = toDate
                objs = objs.filter(date__range=(min_dt, max_dt))
            elif 'datetime'  in fnameList:
                tz = pytz.timezone('Asia/Taipei')
                min_dt = tz.localize(datetime.datetime.combine(fromDate, datetime.time.min))
                max_dt = tz.localize(datetime.datetime.combine(toDate, datetime.time.max))
                objs = objs.filter(datetime__range=(min_dt, max_dt))

        status = inquiry.cleaned_data['status']
        if status:
            if 'status' in fnameList:
                objs = objs.filter(status__code__in = status)

        person = inquiry.cleaned_data['person']
        if person: # contain str
            if objs.model is Person:
                objs = objs.filter(name__icontains = person)
            elif 'person' in fnameList:
                objs = objs.filter(person__name__icontains = person)
    else:
        if afterShow:
            tz = pytz.timezone('Asia/Taipei')
            afterdate = tz.localize(datetime.datetime.now() - datetime.timedelta(days=3))
            if 'date' in fnameList:
                objs = objs.filter(date__gte=afterdate)
            elif 'datetime'  in fnameList:
                objs = objs.filter(datetime__gte=afterdate)


    return objs


# get obj data by table heads
def getRowDatas(obj, tableHeads):
    rowDatas = []
    obj_names = {f.verbose_name:f.name for f in obj._meta.fields}
    for tableHead in tableHeads:
        if tableHead == '料號':
            if obj.partNumber:
                rowDatas += [obj.partNumber]
            elif obj.partNumber_once:
                rowDatas += [obj.partNumber_once]
            else:
                rowDatas += [obj.partNumber_old]
        elif tableHead == '種類':
            if type(obj) is Good:
                rowDatas += [obj.kind.name]
            else:
                rowDatas += [getattr(obj, obj_names[tableHead])]
        elif tableHead == '狀態':
            if type(obj) is GoodWastage:
                rowDatas += [obj.status.name]
            else:
                rowDatas += [getattr(obj, obj_names[tableHead])]
        elif obj_names[tableHead] == 'datetime':
            tz = pytz.timezone('Asia/Taipei')
            datetimeEX = getattr(obj,obj_names[tableHead]).astimezone(tz)
            rowDatas += [datetimeEX.strftime('%Y/%m/%d %H:%M')]
        elif tableHead in obj_names:
            rowDatas += [getattr(obj,obj_names[tableHead])]
        else:
            rowDatas += [tableHead]


    return rowDatas


def noneToZero(number):
    if not number:
        number = 0

    return number


def findkey(dic, value):
    key = None
    for k in dic:
        if dic[k] == value:
            key = k
            break

    return key


#for test
def test(request):
    return render(request, 'test/3.html', locals())


def overview(request):
    global alldatas
    nbar_now = 'overview'
    title = 'Overview'
    caption = '項目總覽'
    overviewToolCaption = '治具總覽'
    overviewCableCaption = '線材總覽'
    have_department = True

    # overview
    overviewTableheads = [GoodInventory._meta.get_field_by_name(f.name)[0].verbose_name \
                        for f in GoodInventory._meta.fields if f.name not in ['id', 'good', 'remark', 'who']]
    i = overviewTableheads.index('數量')
    overviewTableheads[i] = '庫存數量'
    # 移除'進貨中'
    overviewTableheads.extend(['持有數量', '淨領用量', '遺失數量', '遺失比例 (%)', '報廢數量', '報廢比例 (%)'])

    overviewToolTableheads = overviewTableheads
    overviewCableTableheads = overviewTableheads

    overviewToolTabledatas = None
    overviewCableTabledatas = None

    for kind in GoodKind.objects.all():
        overviewTabledatas = []
        for department in Department.objects.all():
            req = noneToZero(GoodRequisition.objects.filter(person__department = department, good__kind = kind).aggregate(Sum('quantity'))['quantity__sum'])
            back = noneToZero(GoodBack.objects.filter(person__department = department, good__kind = kind).aggregate(Sum('quantity'))['quantity__sum'])
            wastage = noneToZero(GoodWastage.objects.filter(person__department = department, good__kind = kind).aggregate(Sum('quantity'))['quantity__sum'])
            used = req - back - wastage
            lost = noneToZero(GoodWastage.objects.filter(person__department = department, status__name = '遺失', good__kind = kind).aggregate(Sum('quantity'))['quantity__sum'])
            scraped = noneToZero(GoodWastage.objects.filter(person__department = department, status__name = '報廢', good__kind = kind).aggregate(Sum('quantity'))['quantity__sum'])

            inventory_total = noneToZero(department.goodinventory_set.filter(good__kind = kind).aggregate(Sum('quantity'))['quantity__sum'])
            inventory_future = noneToZero(GoodBuy.objects.filter(person__department = department, date__gt=datetime.datetime.now(), good__kind = kind).aggregate(Sum('quantity'))['quantity__sum'])

            try:
                overviewTabledatas += [[department.name,
                                        inventory_total - inventory_future,
                                        used,
                                        req - back,
                                        lost,
                                        '{:.2f}'.format(lost/(req - back)*100),
                                        scraped,
                                        '{:.2f}'.format(scraped/(req - back)*100),
                                        ]]
            except ZeroDivisionError:
                overviewTabledatas += [[department.name,
                                        inventory_total - inventory_future,
                                        used,
                                        req - back,
                                        lost,
                                        '0.00',
                                        scraped,
                                        '0.00',
                                        ]]

        if kind.name == '治具':
            overviewToolTabledatas = overviewTabledatas
        elif kind.name == '線材':
            overviewCableTabledatas = overviewTabledatas


    # raw data
    tableheads = ['種類', '型號', '料號', '部門', '持有數量', '淨領用量', '遺失數量', '遺失比例 (%)', '報廢數量', '報廢比例 (%)']
    if 'ok' in request.GET:
        inquiry = GoodInquiryForm(request.GET)

        if not request.GET.get('page') or alldatas['name'] != title:
            alldatas['name'] = title
            alldatas['data'] = []

            for good in objsInquiryFilter(Good.objects.all(), inquiry):
                for department in objsInquiryFilter(Department.objects.all(), inquiry):
                    req = noneToZero(objsInquiryFilter(good.goodrequisition_set.filter(person__department = department), inquiry).aggregate(Sum('quantity'))['quantity__sum'])
                    back = noneToZero(objsInquiryFilter(good.goodback_set.filter(person__department = department), inquiry).aggregate(Sum('quantity'))['quantity__sum'])
                    wastage = noneToZero(objsInquiryFilter(good.goodwastage_set.filter(person__department = department), inquiry).aggregate(Sum('quantity'))['quantity__sum'])
                    used = req - back - wastage

                    lost = noneToZero(objsInquiryFilter(good.goodwastage_set.filter(person__department = department, status__name = '報廢'), inquiry).aggregate(Sum('quantity'))['quantity__sum'])
                    scraped = noneToZero(objsInquiryFilter(good.goodwastage_set.filter(person__department = department, status__name = '遺失'), inquiry).aggregate(Sum('quantity'))['quantity__sum'])

                    inventory_total = noneToZero(good.goodinventory_set.filter(department = department).aggregate(Sum('quantity'))['quantity__sum'])
                    tz = pytz.timezone('Asia/Taipei')
                    inventory_future = noneToZero(good.goodbuy_set.filter(date__gt=datetime.datetime.now(), person__department = department).aggregate(Sum('quantity'))['quantity__sum'])

                    if used > 0 or lost > 0 or scraped > 0:
                        try:
                            alldatas['data'] += [getRowDatas(good, tableheads[:3])
                                        + [department.name, used, req - back,
                                            lost, '{:.2f}'.format(lost/(req - back)*100),
                                            scraped, '{:.2f}'.format(scraped/(req - back)*100),]]
                        except ZeroDivisionError:
                            alldatas['data'] += [getRowDatas(good, tableheads[:3])
                                        + [department.name, used, req - back,
                                            lost, '0.00',
                                            scraped, '0.00']]

        if request.GET['inquiry'] == '下載':
            return streaming_csv_download([tableheads]+alldatas['data'])

        page = page_setting(alldatas['data'], request.GET.get('page'))
        tabledatas = page.object_list
    else:
        inquiry = GoodInquiryForm()

    get = request.GET.copy()
    try:
        get.pop('page')
    except KeyError:
        pass
    search = get.urlencode()
    search = '&' + search if search else ''

    return render(request, 'overview.html',locals())


def ownerView(request):
    global alldatas
    nbar_now = 'ownerView'
    title = 'OwnerView'
    caption = '持有'
    have_department = True
    have_person = True
    tableheads = ['種類', '型號', '料號', '部門', '持有人', '持有', '領用', '歸還', '耗損']

    if 'ok' in request.GET:
        inquiry = GoodInquiryForm(request.GET)

        if not request.GET.get('page') or alldatas['name'] != title:
            alldatas['name'] = title
            alldatas['data'] = []

            for person in objsInquiryFilter(Person.objects.all(), inquiry):
                for good in objsInquiryFilter(Good.objects.all(), inquiry):
                    req = noneToZero(person.goodrequisition_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
                    back = noneToZero(person.goodback_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
                    wastage = noneToZero(person.goodwastage_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
                    used = req - back - wastage

                    if req > 0 or back > 0 or wastage > 0 or used > 0:
                        alldatas['data'] += [getRowDatas(good, tableheads[:3]) + [person.department, person.name, used, req, back, wastage]]

        if request.GET['inquiry'] == '下載':
            return streaming_csv_download([tableheads]+alldatas['data'])

        page = page_setting(alldatas['data'], request.GET.get('page'))
        tabledatas = page.object_list
    else:
        inquiry = GoodInquiryForm()

    get = request.GET.copy()
    try:
        get.pop('page')
    except KeyError:
        pass
    search = get.urlencode()
    search = '&' + search if search else ''

    return render(request, 'history.html',locals())


def inventory(request):
    global alldatas
    nbar_now = 'inventory'
    title = 'Inventory'
    caption = '庫存'
    have_department = True

    tableheads = ['種類', '型號', '料號', '部門', '庫存數量', '進貨中']

    if 'ok' in request.GET:
        inquiry = GoodInquiryForm(request.GET)
    else:
        inquiry = GoodInquiryForm()

    if not request.GET.get('page') or alldatas['name'] != title:
        alldatas['name'] = title
        alldatas['data'] = []

        for obj in objsInquiryFilter(GoodInventory.objects.all(), inquiry):
            inventory_total = obj.quantity
            inventory_future = noneToZero(GoodBuy.objects.filter(good = obj.good, date__gt=datetime.datetime.now(), person__department__name = obj.department).aggregate(Sum('quantity'))['quantity__sum'])

            if inventory_total > 0 or inventory_future > 0:
                alldatas['data'] += [getRowDatas(obj.good,tableheads[:3]) + getRowDatas(obj, [tableheads[3]]) + [inventory_total-inventory_future, inventory_future]]

    if 'ok' in request.GET:
        if request.GET['inquiry'] == '下載':
            return streaming_csv_download([tableheads]+alldatas['data'])

    page = page_setting(alldatas['data'], request.GET.get('page'))
    tabledatas = page.object_list

    get = request.GET.copy()
    try:
        get.pop('page')
    except KeyError:
        pass
    search = get.urlencode()
    search = '&' + search if search else ''

    return render(request, 'history.html',locals())


def allocate(request):
    nbar_now = 'allocate'
    title = 'Allocate'
    caption = '調撥'
    errors = []

    people = [person.__str__() for person in Person.objects.all()]
    if noneToZero(GoodInventory.objects.all().aggregate(Sum('quantity'))['quantity__sum']) > 0:
        goods = [good for good in Good.objects.all()]
    else:
        errors += ['沒治具可調囉']

    if 'ok' in request.GET or 'good_type' in request.POST:
        goodtype = request.POST['good_type']
        f = GoodAllocateForm(request.POST)
    else:
        f = GoodAllocateForm()

    if f.is_valid() and 'good_type' in request.POST:
        try:
            good = Good.objects.get(type = request.POST['good_type'])
        except Good.DoesNotExist:
            errors += ['無此治具"{}"'.format(request.POST['good_type'])]
        except Good.MultipleObjectsReturned:
            errors += ['治具"{}"名字重覆，請告知窗口修正'.format(request.POST['good_type'])]

        quantity = f.cleaned_data['quantity']
        fromDepartment = f.cleaned_data['fromDepartment']
        personEx = f.cleaned_data['personEx']
        toDepartment = f.cleaned_data['toDepartment']
        datetimeEX = f.cleaned_data['datetime']
        remark = f.cleaned_data['remark']

        person, created = Person.objects.get_or_create(name = personEx.split(':')[1].strip(), department = fromDepartment)

        if not errors:
            try:
                gifrom = GoodInventory.objects.get(department = fromDepartment, good = good)

                tz = pytz.timezone('Asia/Taipei')
                inventory_future = noneToZero(good.goodbuy_set.filter(person__department = fromDepartment, date__gt = datetime.datetime.now()).aggregate(Sum('quantity'))['quantity__sum'])

                if quantity > gifrom.quantity - inventory_future:
                    errors += ['{}數量只剩 {}，無法調撥'.format(fromDepartment.name, gifrom.quantity-inventory_future)]

            except GoodInventory.DoesNotExist:
                errors += ['{}數量為 0，無法調撥'.format(fromDepartment.name)]


        if not errors:
            try:
                who = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]
            except:
                who = request.META['REMOTE_ADDR']

            gifrom.quantity -= quantity
            gifrom.save()

            gito, created = GoodInventory.objects.get_or_create(department = toDepartment, good = good, defaults={'quantity':quantity, 'remark':'', 'who':'allocateAuto'})
            if not created:
                gito.quantity += quantity
                gito.save()

            GoodAllocate.objects.create(good = good, person = person, toDepartment = toDepartment, datetime = datetimeEX, quantity = quantity, remark = remark, who = who)

            f = GoodAllocateForm()

            return redirect(reverse("goodsManage_allocateHistory"))

    return render(request, 'inputForm.html',locals())


def allocateHistory(request):
    global alldatas
    nbar_now = 'allocate'
    title = 'Allocate History'
    caption = '調撥歷史'
    have_function = True
    have_date = True
    have_person = True
    have_department = True
    have_toDepartment = True

    function_url = request.path.replace('History','')

    tableheads = ['種類', '型號', '料號', '調出部門', '調出人', '調入部門', '調撥日期', '數量', '備註']

    if 'ok' in request.GET:
        inquiry = GoodInquiryForm(request.GET)
    else:
        inquiry = GoodInquiryForm()

    if not request.GET.get('page') or alldatas['name'] != title:
        alldatas['name'] = title
        alldatas['data'] = []

        for obj in objsInquiryFilter(GoodAllocate.objects.all(), inquiry, afterShow=True):
            if obj.quantity > 0:
                alldatas['data'] += [getRowDatas(obj.good,tableheads[:3]) + [obj.person.department.name, obj.person.name] + getRowDatas(obj, tableheads[5:])]

    if 'ok' in request.GET:
        if request.GET['inquiry'] == '下載':
            return streaming_csv_download([tableheads]+alldatas['data'])

    page = page_setting(alldatas['data'], request.GET.get('page'))
    tabledatas = page.object_list

    get = request.GET.copy()
    try:
        get.pop('page')
    except KeyError:
        pass
    search = get.urlencode()
    search = '&' + search if search else ''

    return render(request, 'history.html',locals())


def buy(request):
    nbar_now = 'buy'
    title = 'Buy'
    caption = '購買'
    errors = []
    people = [person.__str__() for person in Person.objects.all()]
    goods = [good for good in Good.objects.all()]

    if 'ok' in request.GET or 'good_type' in request.POST:
        goodtype = request.POST['good_type']
        f = GoodBuyForm(request.POST)
    else:
        f = GoodBuyForm()

    if f.is_valid() and 'good_type' in request.POST:
        try:
            good = Good.objects.get(type = request.POST['good_type'])
        except Good.DoesNotExist:
            errors += ['無此治具"{}"'.format(request.POST['good_type'])]
        except Good.MultipleObjectsReturned:
            errors += ['治具"{}"名字重覆，請告知窗口修正'.format(request.POST['good_type'])]

        quantity = f.cleaned_data['quantity']
        department = f.cleaned_data['department']
        personEx = f.cleaned_data['personEx']
        date = f.cleaned_data['date']
        pr = f.cleaned_data['pr']
        po = f.cleaned_data['po']
        remark = f.cleaned_data['remark']

        person, created = Person.objects.get_or_create(name = personEx.split(':')[1].strip(), department = department)

        if not errors:
            try:
                who = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]
            except:
                who = request.META['REMOTE_ADDR']

            gi, created = GoodInventory.objects.get_or_create(department = department, good = good, defaults={'quantity':quantity, 'remark':'', 'who':'buyAuto'})

            if not created:
                gi.quantity += quantity
                gi.save()

            gb = GoodBuy.objects.create(good=good, person=person, date=date, quantity=quantity, pr=pr, po=po, remark=remark, who=who)

            f = GoodBuyForm()
            return redirect(reverse("goodsManage_buyHistory"))

    return render(request, 'inputForm.html',locals())


def buyHistory(request):
    global alldatas
    nbar_now = 'buy'
    title = 'Buy History'
    caption = '購買歷史'
    have_department = True
    have_function = True
    have_date = True
    have_person = True

    function_url = request.path.replace('History','')

    tableheads = ['種類', '型號', '料號', '部門', '購買人', '入料日期', '數量', 'PR', 'PO', '備註']

    if 'ok' in request.GET:
        inquiry = GoodInquiryForm(request.GET)
    else:
        inquiry = GoodInquiryForm()

    if not request.GET.get('page') or alldatas['name'] != title:
        alldatas['name'] = title
        alldatas['data'] = []

        for obj in objsInquiryFilter(GoodBuy.objects.all(), inquiry, afterShow=True):
            if obj.quantity > 0:
                alldatas['data'] += [getRowDatas(obj.good,tableheads[:3]) + [obj.person.department.name, obj.person.name] + getRowDatas(obj, tableheads[5:])]

    if 'ok' in request.GET:
        if request.GET['inquiry'] == '下載':
            return streaming_csv_download([tableheads]+alldatas['data'])

    page = page_setting(alldatas['data'], request.GET.get('page'))
    tabledatas = page.object_list

    get = request.GET.copy()
    try:
        get.pop('page')
    except KeyError:
        pass
    search = get.urlencode()
    search = '&' + search if search else ''

    return render(request, 'history.html',locals())


def back(request):
    nbar_now = 'back'
    title = 'Back'
    caption = '歸還'
    errors = []
    people = [person.__str__() for person in Person.objects.all()]
    goods = [good for good in Good.objects.all()]

    if 'ok' in request.GET or 'good_type' in request.POST:
        goodtype = request.POST['good_type']
        f = GoodBackForm(request.POST)
    else:
        f = GoodBackForm()

    if f.is_valid() and 'good_type' in request.POST:
        try:
            good = Good.objects.get(type = request.POST['good_type'])
        except Good.DoesNotExist:
            errors += ['無此治具"{}"'.format(request.POST['good_type'])]
        except Good.MultipleObjectsReturned:
            errors += ['治具"{}"名字重覆，請告知窗口修正'.format(request.POST['good_type'])]

        quantity = f.cleaned_data['quantity']
        department = f.cleaned_data['department']
        personEx = f.cleaned_data['personEx']
        datetimeEX = f.cleaned_data['datetime']
        remark = f.cleaned_data['remark']

        person, created = Person.objects.get_or_create(name = personEx.split(':')[1].strip(), department = department)

        if not errors:
            req = noneToZero(person.goodrequisition_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            back = noneToZero(person.goodback_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            wastage = noneToZero(person.goodwastage_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            used = req - back - wastage

            if quantity > used:
                errors += ['%s持有數量只有 %d，無法歸還' %(person, used)]

        if not errors:
            try:
                who = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]
            except:
                who = request.META['REMOTE_ADDR']

            gi, created = GoodInventory.objects.get_or_create(department=department, good = good, defaults={'quantity':quantity, 'remark':'', 'who':'backAuto'})
            if not created:
                gi.quantity += quantity
                gi.save()
            gb = GoodBack.objects.create(good=good, person=person, datetime=datetimeEX, quantity=quantity, remark=remark, who=who)

            f = GoodBackForm()
            return redirect(reverse("goodsManage_backHistory"))

    return render(request, 'inputForm.html',locals())


def backOuter(request):
    nbar_now = 'back'
    title = 'Back Outer'
    caption = '歸還'
    errors = []
    people = [person.__str__() for person in Person.objects.all()]
    goods = [good for good in Good.objects.all()]

    if 'ok' in request.GET or 'good_type' in request.POST:
        goodtype = request.POST['good_type']
        f = GoodBackOuterForm(request.POST)
    else:
        f = GoodBackOuterForm()

    if f.is_valid() and 'good_type' in request.POST:
        try:
            good = Good.objects.get(type = request.POST['good_type'])
        except Good.DoesNotExist:
            errors += ['無此治具"{}"'.format(request.POST['good_type'])]
        except Good.MultipleObjectsReturned:
            errors += ['治具"{}"名字重覆，請告知窗口修正'.format(request.POST['good_type'])]

        quantity = f.cleaned_data['quantity']
        department = f.cleaned_data['department']
        personEx = f.cleaned_data['personEx']
        datetimeEX = f.cleaned_data['datetime']
        remark = f.cleaned_data['remark']
        toDepartment = f.cleaned_data['toDepartment']

        person, created = Person.objects.get_or_create(name = personEx.split(':')[1].strip(), department = department)

        if not errors:
            req = noneToZero(person.goodrequisition_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            back = noneToZero(person.goodback_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            wastage = noneToZero(person.goodwastage_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            used = req - back - wastage

            if quantity > used:
                errors += ['%s持有數量只有 %d，無法歸還' %(person, used)]

        if not errors:
            try:
                who = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]
            except:
                who = request.META['REMOTE_ADDR']

            gb = GoodBack.objects.create(good=good, person=person, datetime=datetimeEX, quantity=quantity, remark=remark, who=who)

            gito, created = GoodInventory.objects.get_or_create(department = toDepartment, good = good, defaults={'quantity':quantity, 'remark':'', 'who':'allocateAuto'})
            if not created:
                gito.quantity += quantity
                gito.save()

            ga = GoodAllocate.objects.create(good = good, person = person, toDepartment = toDepartment, datetime = datetimeEX, quantity = quantity, remark = remark, who = who)

            f = GoodBackOuterForm()
            return redirect(reverse("goodsManage_backHistory"))

    return render(request, 'inputForm.html',locals())


def backHistory(request):
    global alldatas
    nbar_now = 'back'
    title = 'Back History'
    caption = '歸還歷史'
    have_department = True
    have_function = True
    have_date = True
    have_person = True

    function_url = request.path.replace('History','')

    tableheads = ['種類', '型號', '料號', '部門', '歸還人', '歸還日期', '數量', '備註']

    if 'ok' in request.GET:
        inquiry = GoodInquiryForm(request.GET)
    else:
        inquiry = GoodInquiryForm()

    if not request.GET.get('page') or alldatas['name'] != title:
        alldatas['name'] = title
        alldatas['data'] = []

        for obj in objsInquiryFilter(GoodBack.objects.all(), inquiry, afterShow=True):
            if obj.quantity > 0:
                alldatas['data'] += [getRowDatas(obj.good,tableheads[:3]) + [obj.person.department.name, obj.person.name] + getRowDatas(obj, tableheads[5:])]

    if 'ok' in request.GET:
        if request.GET['inquiry'] == '下載':
            return streaming_csv_download([tableheads]+alldatas['data'])

    page = page_setting(alldatas['data'], request.GET.get('page'))
    tabledatas = page.object_list

    get = request.GET.copy()
    try:
        get.pop('page')
    except KeyError:
        pass
    search = get.urlencode()
    search = '&' + search if search else ''

    return render(request, 'history.html',locals())


def requisition(request):
    nbar_now = 'requisition'
    title = 'Requisition'
    caption = '領用'
    errors = []
    people = [person.__str__() for person in Person.objects.all()]
    if noneToZero(GoodInventory.objects.all().aggregate(Sum('quantity'))['quantity__sum']) > 0:
        goods = [good for good in Good.objects.all()]
    else:
        errors += ['治具已清空，下次請早']

    if 'ok' in request.GET or 'good_type' in request.POST:
        goodtype = request.POST['good_type']
        f = GoodRequisitionForm(request.POST)
    else:
        f = GoodRequisitionForm()

    if f.is_valid() and 'good_type' in request.POST:
        try:
            good = Good.objects.get(type = request.POST['good_type'])
        except Good.DoesNotExist:
            errors += ['無此治具"{}"'.format(request.POST['good_type'])]
        except Good.MultipleObjectsReturned:
            errors += ['治具"{}"名字重覆，請告知窗口修正'.format(request.POST['good_type'])]

        quantity = f.cleaned_data['quantity']
        department = f.cleaned_data['department']
        personEx = f.cleaned_data['personEx']
        datetimeEX = f.cleaned_data['datetime']
        remark = f.cleaned_data['remark']

        person, created = Person.objects.get_or_create(name = personEx.split(':')[1].strip(), department = department)

        if not errors:
            try:
                gi = GoodInventory.objects.get(department=department, good = good)

                inventory_future = noneToZero(GoodBuy.objects.filter(good = good, person__department = department, date__gt = datetime.datetime.now()).aggregate(Sum('quantity'))['quantity__sum'])

                if quantity > gi.quantity-inventory_future:
                    errors += ['{0}數量只剩 {1}，無法領取 '.format(department.name, gi.quantity-inventory_future)]

            except GoodInventory.DoesNotExist:
                errors += ['{0}數量為 0，無法領取'.format(department.name)]

        if not errors:
            req = noneToZero(person.goodrequisition_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            back = noneToZero(person.goodback_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            wastage = noneToZero(person.goodwastage_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            used = req - back - wastage

            if used > 0:
                have_warning = True
                warning = {}
                if request.POST.get('warningCheck') == 'OK':
                    have_warning = False
                    pass
                else:
                    errors += ['請確認是否領取，OK 打勾']
                    warning['label'] = '警告'
                    warning['txt'] = '{0} 已持有數量 {1}'.format(person, used)

        if not errors:
            try:
                who = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]
            except:
                who = request.META['REMOTE_ADDR']

            gi.quantity -= quantity
            gi.save()

            gr = GoodRequisition.objects.create(good=good, person=person, datetime=datetimeEX, quantity=quantity, remark=remark, who=who)

            f = GoodRequisitionForm()
            return redirect(reverse("goodsManage_requisitionHistory"))



    return render(request, 'inputForm.html',locals())


def requisitionOuter(request):
    nbar_now = 'requisition'
    title = 'Requisition Outer'
    caption = '領用'
    errors = []
    people = [person.__str__() for person in Person.objects.all()]
    if noneToZero(GoodInventory.objects.all().aggregate(Sum('quantity'))['quantity__sum']) > 0:
        goods = [good for good in Good.objects.all()]
    else:
        errors += ['治具已清空，下次請早']

    if 'ok' in request.GET or 'good_type' in request.POST:
        goodtype = request.POST['good_type']
        f = GoodRequisitionOuterForm(request.POST)
    else:
        f = GoodRequisitionOuterForm()

    if f.is_valid() and 'good_type' in request.POST:
        try:
            good = Good.objects.get(type = request.POST['good_type'])
        except Good.DoesNotExist:
            errors += ['無此治具"{}"'.format(request.POST['good_type'])]
        except Good.MultipleObjectsReturned:
            errors += ['治具"{}"名字重覆，請告知窗口修正'.format(request.POST['good_type'])]

        quantity = f.cleaned_data['quantity']
        fromDepartment = f.cleaned_data['fromDepartment']
        personFromEx = f.cleaned_data['personFromEx']
        department = f.cleaned_data['department']
        personEx = f.cleaned_data['personEx']
        datetimeEX = f.cleaned_data['datetime']
        remark = f.cleaned_data['remark']

        person, created = Person.objects.get_or_create(name = personEx.split(':')[1].strip(), department = department)
        personFrom, created = Person.objects.get_or_create(name = personFromEx.split(':')[1].strip(), department = fromDepartment)

        if not errors:
            try:
                gifrom = GoodInventory.objects.get(department = fromDepartment, good = good)

                tz = pytz.timezone('Asia/Taipei')
                inventory_future = noneToZero(good.goodbuy_set.filter(person__department = fromDepartment, date__gt = datetime.datetime.now()).aggregate(Sum('quantity'))['quantity__sum'])

                if quantity > gifrom.quantity - inventory_future:
                    errors += ['{}數量只剩 {}，無法調撥領用'.format(fromDepartment.name, gifrom.quantity-inventory_future)]

            except GoodInventory.DoesNotExist:
                errors += ['{}數量為 0，無法調撥領用'.format(fromDepartment.name)]

        if not errors:
            req = noneToZero(person.goodrequisition_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            back = noneToZero(person.goodback_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            wastage = noneToZero(person.goodwastage_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            used = req - back - wastage

            if used > 0:
                have_warning = True
                warning = {}
                if request.POST.get('warningCheck') == 'OK':
                    have_warning = False
                    pass
                else:
                    errors += ['請確認是否領取，OK 打勾']
                    warning['label'] = '警告'
                    warning['txt'] = '{0} 已持有數量 {1}'.format(person, used)

        if not errors:
            try:
                who = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]
            except:
                who = request.META['REMOTE_ADDR']

            gifrom.quantity -= quantity
            gifrom.save()

            ga = GoodAllocate.objects.create(good = good, person = personFrom, toDepartment = department, datetime = datetimeEX, quantity = quantity, remark = remark, who = who)
            gr = GoodRequisition.objects.create(good=good, person=person, datetime=datetimeEX, quantity=quantity, remark=remark, who=who)

            f = GoodRequisitionOuterForm()
            return redirect(reverse("goodsManage_requisitionHistory"))


    return render(request, 'inputForm.html',locals())


def requisitionHistory(request):
    global alldatas
    nbar_now = 'requisition'
    title = 'Requisition History'
    caption = '領用歷史'
    have_department = True
    have_function = True
    have_date = True
    have_person = True

    function_url = request.path.replace('History','')

    tableheads = ['種類', '型號', '料號', '部門', '領用人', '領用日期', '數量', '備註']

    if 'ok' in request.GET:
        inquiry = GoodInquiryForm(request.GET)
    else:
        inquiry = GoodInquiryForm()

    if not request.GET.get('page') or alldatas['name'] != title:
        alldatas['name'] = title
        alldatas['data'] = []
        for obj in objsInquiryFilter(GoodRequisition.objects.all(), inquiry, afterShow=True):
            if obj.quantity > 0:
                alldatas['data'] += [getRowDatas(obj.good,tableheads[:3]) + [obj.person.department.name, obj.person.name] + getRowDatas(obj, tableheads[5:])]

    if 'ok' in request.GET:
        if request.GET['inquiry'] == '下載':
            return streaming_csv_download([tableheads]+alldatas['data'])

    page = page_setting(alldatas['data'], request.GET.get('page'))
    tabledatas = page.object_list

    get = request.GET.copy()
    try:
        get.pop('page')
    except KeyError:
        pass
    search = get.urlencode()
    search = '&' + search if search else ''

    return render(request, 'history.html', locals())


def wastage(request):
    nbar_now = 'wastage'
    title = 'Wastage'
    caption = '耗損'
    errors = []
    people = [person.__str__() for person in Person.objects.all()]
    goods = [good for good in Good.objects.all()]

    if 'ok' in request.GET or 'good_type' in request.POST:
        goodtype = request.POST['good_type']
        f = GoodWastageForm(request.POST)
    else:
        f = GoodWastageForm()

    if f.is_valid() and 'good_type' in request.POST:
        try:
            good = Good.objects.get(type = request.POST['good_type'])
        except Good.DoesNotExist:
            errors += ['無此治具"{}"'.format(request.POST['good_type'])]
        except Good.MultipleObjectsReturned:
            errors += ['治具"{}"名字重覆，請告知窗口修正'.format(request.POST['good_type'])]

        quantity = f.cleaned_data['quantity']
        department = f.cleaned_data['department']
        personEx = f.cleaned_data['personEx']
        status = f.cleaned_data['status']
        datetimeEX = f.cleaned_data['datetime']
        remark = f.cleaned_data['remark']

        person, created = Person.objects.get_or_create(name = personEx.split(':')[1].strip(), department = department)

        if not errors:
            req = noneToZero(person.goodrequisition_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            back = noneToZero(person.goodback_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            wastage = noneToZero(person.goodwastage_set.filter(good = good).aggregate(Sum('quantity'))['quantity__sum'])
            used = req - back - wastage

            if quantity > used:
                errors += ['%s持有數量只有 %d，無法耗損' %(person, used)]

        if not errors:
            try:
                who = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]
            except:
                who = request.META['REMOTE_ADDR']

            gw = GoodWastage.objects.create(good=good, person=person, datetime=datetimeEX, quantity=quantity, status=status, remark=remark, who=who)

            f = GoodWastageForm()
            return redirect(reverse("goodsManage_wastageHistory"))

    return render(request, 'inputForm.html',locals())


def wastageHistory(request):
    global alldatas
    nbar_now = 'wastage'
    title = 'Wastage History'
    caption = '耗損歷史'
    have_department = True
    have_function = True
    have_date = True
    have_status = True
    have_person = True

    function_url = request.path.replace('History','')

    tableheads = ['種類', '型號', '料號', '部門', '耗損人', '耗損日期', '數量', '狀態', '備註']

    if 'ok' in request.GET:
        inquiry = GoodInquiryForm(request.GET)
    else:
        inquiry = GoodInquiryForm()

    if not request.GET.get('page') or alldatas['name'] != title:
        alldatas['name'] = title
        alldatas['data'] = []
        for obj in objsInquiryFilter(GoodWastage.objects.all(), inquiry, afterShow=True):
            if obj.quantity > 0:
                alldatas['data'] += [getRowDatas(obj.good,tableheads[:3]) + [obj.person.department.name, obj.person.name] + getRowDatas(obj, tableheads[5:])]

    if 'ok' in request.GET:
        if request.GET['inquiry'] == '下載':
            return streaming_csv_download([tableheads]+alldatas['data'])

    page = page_setting(alldatas['data'], request.GET.get('page'))
    tabledatas = page.object_list

    get = request.GET.copy()
    try:
        get.pop('page')
    except KeyError:
        pass
    search = get.urlencode()
    search = '&' + search if search else ''

    return render(request, 'history.html',locals())


def repair(request):
    nbar_now = 'repair'
    title = 'Repair'
    caption = '維修'
    errors = []
    people = [person.__str__() for person in Person.objects.all()]
    goods = [good for good in Good.objects.all()]

    if 'ok' in request.GET or 'good_type' in request.POST:
        goodtype = request.POST['good_type']
        f = GoodRepairForm(request.POST)
    else:
        f = GoodRepairForm()

    if f.is_valid() and 'good_type' in request.POST:
        try:
            good = Good.objects.get(type = request.POST['good_type'])
        except Good.DoesNotExist:
            errors += ['無此治具"{}"'.format(request.POST['good_type'])]
        except Good.MultipleObjectsReturned:
            errors += ['治具"{}"名字重覆，請告知窗口修正'.format(request.POST['good_type'])]

        quantity = f.cleaned_data['quantity']
        department = f.cleaned_data['department']
        personEx = f.cleaned_data['personEx']
        date = f.cleaned_data['date']
        remark = f.cleaned_data['remark']

        person, created = Person.objects.get_or_create(name = personEx.split(':')[1].strip(), department = department)

        if not errors:
            wastage_quantity = noneToZero(good.goodwastage_set.filter(person__department = department, status__code = '01').aggregate(Sum('quantity'))['quantity__sum'])
            repaired_quantity = noneToZero(good.goodrepair_set.filter(person__department = department).aggregate(Sum('quantity'))['quantity__sum'])

            if  quantity > wastage_quantity - repaired_quantity:
                errors += ['{0} : 維修數量 {1} > 報廢數量 {2}'.format(request.POST['good_type'], quantity, wastage_quantity - repaired_quantity)]

        if not errors:
            try:
                who = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]
            except:
                who = request.META['REMOTE_ADDR']

            gi, created = GoodInventory.objects.get_or_create(department = department, good = good, defaults={'quantity':quantity, 'remark':'', 'who':'buyAuto'})

            if not created:
                gi.quantity += quantity
                gi.save()

            gb = GoodRepair.objects.create(good=good, person=person, date=date, quantity=quantity, remark=remark, who=who)

            f = GoodRepairForm()
            return redirect(reverse("goodsManage_repairHistory"))

    return render(request, 'inputForm.html',locals())


def repairHistory(request):
    global alldatas
    nbar_now = 'repair'
    title = 'Repair History'
    caption = '維修歷史'
    have_department = True
    have_function = True
    have_date = True
    have_person = True

    function_url = request.path.replace('History','')

    tableheads = ['種類', '型號', '料號', '部門', '維修人', '維修日期', '數量', '備註']

    if 'ok' in request.GET:
        inquiry = GoodInquiryForm(request.GET)
    else:
        inquiry = GoodInquiryForm()

    if not request.GET.get('page') or alldatas['name'] != title:
        alldatas['name'] = title
        alldatas['data'] = []

        for obj in objsInquiryFilter(GoodRepair.objects.all(), inquiry, afterShow=True):
            if obj.quantity > 0:
                alldatas['data'] += [getRowDatas(obj.good,tableheads[:3]) + [obj.person.department.name, obj.person.name] + getRowDatas(obj, tableheads[5:])]

    if 'ok' in request.GET:
        if request.GET['inquiry'] == '下載':
            return streaming_csv_download([tableheads]+alldatas['data'])

    page = page_setting(alldatas['data'], request.GET.get('page'))
    tabledatas = page.object_list

    get = request.GET.copy()
    try:
        get.pop('page')
    except KeyError:
        pass
    search = get.urlencode()
    search = '&' + search if search else ''

    return render(request, 'history.html',locals())


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value.encode('BIG5')


def streaming_csv_download(rdatas):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    #rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(rdata) for rdata in rdatas), content_type = "text/csv")
    response['Content-Disposition'] = 'attachment; filename="data.csv"'
    return response
