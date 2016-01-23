from django.contrib import admin

# Register your models here.
from goodsManage.models import *

class GoodInventoryInline(admin.TabularInline):
    model = GoodInventory
    extra = 1

@admin.register(GoodKind)
class GoodKindAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GoodKind._meta.fields if f.name != 'id']
    
@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Good._meta.fields if f.name != 'id']
    list_filter = ('kind',)
    search_fields = ('partNumber', 'partNumber_once', 'partNumber_old', 'type' )
    inlines = (GoodInventoryInline,)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Department._meta.fields if f.name != 'id']

    
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Person._meta.fields if f.name != 'id']
    list_filter = ('department',)
    search_fields = ('name',)
    
@admin.register(GoodInventory)
class GoodInventoryAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GoodInventory._meta.fields if f.name != 'id']
    list_filter = ('department', 'good__kind',)
    search_fields = ('good__type',)
    
@admin.register(GoodRequisition)
class GoodRequisitionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GoodRequisition._meta.fields if f.name != 'id']
    list_filter = ('datetime', 'person__department', 'good__kind',)
    search_fields = ('good__type',)

@admin.register(GoodBack)
class GoodBackAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GoodBack._meta.fields if f.name != 'id']
    list_filter = ('datetime', 'person__department', 'good__kind',)
    #search_fields = ('person',)

@admin.register(GoodBuy)
class GoodBuyAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GoodBuy._meta.fields if f.name != 'id']
    list_filter = ('date', 'person__department', 'good__kind',)
    #search_fields = ('pr','po')

@admin.register(GoodAllocate)
class GoodAllocateAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GoodAllocate._meta.fields if f.name != 'id']
    list_filter = ('datetime', 'person__department', 'toDepartment', 'good__kind',)
    #search_fields = ('person',)
    
@admin.register(WastageStatus)
class WastageStatusAdmin(admin.ModelAdmin):
    list_display = [f.name for f in WastageStatus._meta.fields if f.name != 'id']
    
@admin.register(GoodWastage)
class GoodWastageAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GoodWastage._meta.fields if f.name != 'id']
    list_filter = ('datetime', 'person__department', 'good__kind',)
    search_fields = ('good__type',)

@admin.register(GoodRepair)
class GoodRepairAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GoodRepair._meta.fields if f.name != 'id']
    list_filter = ('date', 'person__department')