from django.conf.urls import include, url
from .views import *

urlpatterns = [
    url(r'^overview/$', overview, name="goodsManage_overview"),
    url(r'^ownerView/$', ownerView, name="goodsManage_ownerView"),
    url(r'^inventory/$', inventory, name="goodsManage_inventory"),
    url(r'^allocate/$', allocate, name="goodsManage_allocate"),
    url(r'^allocateHistory/$', allocateHistory, name="goodsManage_allocateHistory"),
    url(r'^buy/$', buy, name="goodsManage_buy"),
    url(r'^buyHistory/$', buyHistory, name="goodsManage_buyHistory"),
    url(r'^back/$', back, name="goodsManage_back"),
    url(r'^backOuter/$', backOuter, name="goodsManage_backOuter"),
    url(r'^backHistory/$', backHistory, name="goodsManage_backHistory"),
    url(r'^requisition/$', requisition, name="goodsManage_requisition"),
    url(r'^requisitionOuter/$', requisitionOuter, name="goodsManage_requisitionOuter"),
    url(r'^requisitionHistory/$', requisitionHistory, name="goodsManage_requisitionHistory"),
    url(r'^wastage/$', wastage, name="goodsManage_wastage"),
    url(r'^wastageHistory/$', wastageHistory, name="goodsManage_wastageHistory"),
    url(r'^repair/$', repair, name="goodsManage_repair"),
    url(r'^repairHistory/$', repairHistory, name="goodsManage_repairHistory"),
    # for test
    #url(r'^test/$', test),
]
