from django import forms

# modules from django
from django.forms.extras.widgets import SelectDateWidget

from . import choices
from .models import *
import datetime

class GoodInquiryForm(forms.Form):
    kind = forms.MultipleChoiceField(required = False, label = '種類(可複選)', widget=forms.CheckboxSelectMultiple, choices = choices.KIND_CHOICES)
    department = forms.MultipleChoiceField(required = False, label = '部門(可複選)', widget=forms.CheckboxSelectMultiple, choices = choices.DEPARTMENT_CHOICES_SORTED_ADD_ALL)
    toDepartment = forms.MultipleChoiceField(required = False, label = '調入部門(可複選)', widget=forms.CheckboxSelectMultiple, choices = choices.DEPARTMENT_CHOICES_SORTED_ADD_ALL)
    type = forms.CharField(required = False, widget=forms.TextInput(attrs={'size': '20'}), label = '型號', max_length = 50)
    partNumber = forms.CharField(required = False, label = '料號', widget=forms.TextInput(attrs={'size': '14'}), max_length = 13)
    fromDate = forms.DateField(required = False, label = '起始日期', widget = SelectDateWidget(years = [y for y in range(2015,2030)]),  initial=(datetime.date.today() - datetime.timedelta(days=3)))
    toDate = forms.DateField(required = False, label = '終止日期', widget = SelectDateWidget(years = [y for y in range(2015,2030)]), initial = datetime.date.today())
    status = forms.MultipleChoiceField(required = False, label = '狀態(可複選)', widget = forms.CheckboxSelectMultiple, choices = choices.WASTAGE_STATUS_CHOICES)
    person = forms.CharField(required = False, label = '人名', widget=forms.TextInput(attrs={'size': '5'}), max_length = 6)


class GoodRequisitionForm(forms.ModelForm):
    quantity = forms.IntegerField(label = '數量', min_value = 1)
    department = forms.ModelChoiceField(queryset = Department.objects.all(), label = '領用部門')
    personEx = forms.CharField(label = '領用人', widget=forms.TextInput(attrs={'size': '10', 'onkeyup':"changeList(tempList, 'id_rightList', 'id_rightListSel', $('#id_department option:selected').text(), this.value)", 'onfocus':'this.select();tempList=peopleList;focusID=this.id'}), max_length = 10)

    class Meta:
        model = GoodRequisition
        fields = ['quantity', 'department', 'personEx', 'datetime', 'remark']
        #exclude  = ('good', 'who')
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 22, 'rows': 11}),
        }

    def clean_personEx(self):
        personEx = self.cleaned_data.get('personEx')
        department  = self.cleaned_data.get('department')

        data = personEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif department:
            if data[0].strip() != department.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), department.name))
        return personEx


class GoodRequisitionOuterForm(forms.ModelForm):
    quantity = forms.IntegerField(label = '數量', min_value = 1)
    department = forms.ModelChoiceField(queryset = Department.objects.all(), label = '領用部門')
    personEx = forms.CharField(label = '領用人', widget=forms.TextInput(attrs={'size': '10', 'onkeyup':"changeList(tempList, 'id_rightList', 'id_rightListSel', $('#id_department option:selected').text(), this.value)", 'onfocus':'this.select();tempList=peopleList;focusID=this.id'}), max_length = 10)
    fromDepartment = forms.ModelChoiceField(queryset = Department.objects.all(), label = '調出部門')
    personFromEx = forms.CharField(label = '調撥人', widget=forms.TextInput(attrs={'size': '10', 'onkeyup':"changeList(tempList, 'id_rightList', 'id_rightListSel', $('#id_fromDepartment option:selected').text(), this.value)", 'onfocus':'this.select();tempList=peopleList;focusID=this.id'}), max_length = 10)

    class Meta:
        model = GoodRequisition
        fields = ['quantity', 'fromDepartment', 'personFromEx', 'department', 'personEx', 'datetime', 'remark']
        #exclude  = ('good', 'who')
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 22, 'rows': 11}),
        }

    def clean_department(self):
        fromDepartment = self.cleaned_data.get('fromDepartment')
        department = self.cleaned_data.get('department')

        if fromDepartment == department:
            raise forms.ValidationError('不得為同部門')
        return department

    def clean_personEx(self):
        personEx = self.cleaned_data.get('personEx')
        department  = self.cleaned_data.get('department')

        data = personEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif department:
            if data[0].strip() != department.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), department.name))
        return personEx

    def clean_personFromEx(self):
        personFromEx = self.cleaned_data.get('personFromEx')
        fromDepartment  = self.cleaned_data.get('fromDepartment')

        data = personFromEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif fromDepartment:
            if data[0].strip() != fromDepartment.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), fromDepartment.name))
        return personFromEx


class GoodBackForm(forms.ModelForm):
    quantity = forms.IntegerField(label = '數量', min_value = 1)
    department = forms.ModelChoiceField(queryset = Department.objects.all(), label = '歸還部門')
    personEx = forms.CharField(label = '歸還人', widget=forms.TextInput(attrs={'size': '10', 'onkeyup':"changeList(tempList, 'id_rightList', 'id_rightListSel', $('#id_department option:selected').text(), this.value)", 'onfocus':'this.select();tempList=peopleList;focusID=this.id'}), max_length = 10)

    class Meta:
        model = GoodBack
        fields = ['quantity', 'department', 'personEx', 'datetime', 'remark']
        #exclude  = ('good', 'who')
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 22, 'rows': 11}),
        }

    def clean_personEx(self):
        personEx = self.cleaned_data.get('personEx')
        department  = self.cleaned_data.get('department')

        data = personEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif department:
            if data[0].strip() != department.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), department.name))
        return personEx


class GoodBackOuterForm(forms.ModelForm):
    quantity = forms.IntegerField(label = '數量', min_value = 1)
    department = forms.ModelChoiceField(queryset = Department.objects.all(), label = '歸還部門')
    personEx = forms.CharField(label = '歸還人', widget=forms.TextInput(attrs={'size': '10', 'onkeyup':"changeList(tempList, 'id_rightList', 'id_rightListSel', $('#id_department option:selected').text(), this.value)", 'onfocus':'this.select();tempList=peopleList;focusID=this.id'}), max_length = 10)
    toDepartment = forms.ModelChoiceField(queryset = Department.objects.all(), label = '調入部門')

    class Meta:
        model = GoodBack
        fields = ['quantity', 'department', 'personEx', 'toDepartment', 'datetime', 'remark']
        #exclude  = ('good', 'who')
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 22, 'rows': 11}),
        }

    def clean_toDepartment(self):
        toDepartment = self.cleaned_data.get('toDepartment')
        department = self.cleaned_data.get('department')

        if toDepartment == department:
            raise forms.ValidationError('不得為同部門')
        return toDepartment

    def clean_personEx(self):
        personEx = self.cleaned_data.get('personEx')
        department  = self.cleaned_data.get('department')

        data = personEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif department:
            if data[0].strip() != department.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), department.name))
        return personEx

    def clean_personToEx(self):
        personToEx = self.cleaned_data.get('personToEx')
        toDepartment  = self.cleaned_data.get('toDepartment')

        data = personToEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif toDepartment:
            if data[0].strip() != toDepartment.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), toDepartment.name))
        return personToEx


#class GoodInventoryForm(forms.Form):
#    department = forms.ChoiceField(label = '部門', widget = forms.Select, choices = choices.DEPARTMENT_CHOICES_SORTED)
#    quantity = forms.IntegerField(label = '數量', min_value = 1)
#    remark = forms.CharField(required = False, label = '備註', widget = forms.Textarea(attrs={'cols': 20, 'rows': 10}))


class GoodBuyForm(forms.ModelForm):
    quantity = forms.IntegerField(label = '數量', min_value = 1)
    department = forms.ModelChoiceField(queryset = Department.objects.all(), label = '購買部門')
    personEx = forms.CharField(label = '購買人', widget=forms.TextInput(attrs={'size': '10', 'onkeyup':"changeList(tempList, 'id_rightList', 'id_rightListSel', $('#id_department option:selected').text(), this.value)", 'onfocus':'this.select();tempList=peopleList;focusID=this.id'}), max_length = 10)

    class Meta:
        model = GoodBuy
        fields = ['quantity', 'department', 'personEx', 'date', 'pr', 'po', 'remark']
        #exclude  = ('good', 'who',)
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 20, 'rows': 7}),
        }


    def clean_personEx(self):
        personEx = self.cleaned_data.get('personEx')
        department  = self.cleaned_data.get('department')

        data = personEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif department:
            if data[0].strip() != department.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), department.name))
        return personEx


class GoodAllocateForm(forms.ModelForm):
    quantity = forms.IntegerField(label = '數量', min_value = 1)
    fromDepartment = forms.ModelChoiceField(queryset = Department.objects.all(), label = '調出部門')
    personEx = forms.CharField(label = '調出人', widget=forms.TextInput(attrs={'size': '10', 'onkeyup':"changeList(tempList, 'id_rightList', 'id_rightListSel', $('#id_fromDepartment option:selected').text(), this.value)", 'onfocus':'this.select();tempList=peopleList;focusID=this.id'}), max_length = 10)

    class Meta:
        model = GoodAllocate
        fields = ['quantity', 'fromDepartment', 'personEx', 'toDepartment', 'datetime', 'remark']
        #exclude  = ('good', 'who')
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 20, 'rows': 10}),
        }

    def clean_toDepartment(self):
        fromDepartment = self.cleaned_data.get('fromDepartment')
        toDepartment = self.cleaned_data.get('toDepartment')

        if fromDepartment == toDepartment:
            raise forms.ValidationError('不得為同部門')
        return toDepartment

    def clean_personEx(self):
        personEx = self.cleaned_data.get('personEx')
        fromDepartment  = self.cleaned_data.get('fromDepartment')

        data = personEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif fromDepartment:
            if data[0].strip() != fromDepartment.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), fromDepartment.name))
        return personEx


class GoodWastageForm(forms.ModelForm):
    quantity = forms.IntegerField(label = '數量', min_value = 1)
    department = forms.ModelChoiceField(queryset = Department.objects.all(), label = '耗損部門')
    personEx = forms.CharField(label = '耗損人', widget=forms.TextInput(attrs={'size': '10', 'onkeyup':"changeList(tempList, 'id_rightList', 'id_rightListSel', $('#id_department option:selected').text(), this.value)", 'onfocus':'this.select();tempList=peopleList;focusID=this.id'}), max_length = 10)

    class Meta:
        model = GoodWastage
        fields = ['quantity', 'department', 'personEx', 'status', 'datetime', 'remark']
        #exclude  = ('good', 'who',)
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 20, 'rows': 8}),
        }

    def clean_personEx(self):
        personEx = self.cleaned_data.get('personEx')
        department  = self.cleaned_data.get('department')

        data = personEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif department:
            if data[0].strip() != department.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), department.name))
        return personEx


class GoodRepairForm(forms.ModelForm):
    quantity = forms.IntegerField(label = '數量', min_value = 1)
    department = forms.ModelChoiceField(queryset = Department.objects.all(), label = '維修部門')
    personEx = forms.CharField(label = '維修人', widget=forms.TextInput(attrs={'size': '10', 'onkeyup':"changeList(tempList, 'id_rightList', 'id_rightListSel', $('#id_department option:selected').text(), this.value)", 'onfocus':'this.select();tempList=peopleList;focusID=this.id'}), max_length = 10)

    class Meta:
        model = GoodRepair
        fields = ['quantity', 'department', 'personEx', 'date', 'remark']
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 20, 'rows': 7}),
        }


    def clean_personEx(self):
        personEx = self.cleaned_data.get('personEx')
        department  = self.cleaned_data.get('department')

        data = personEx.split(':')
        if len(data) != 2:
            raise forms.ValidationError('格式錯誤，需為「部門 : 名字」')
        elif department:
            if data[0].strip() != department.name:
                raise forms.ValidationError('部門不一致 ({1}, {0})'.format(data[0].strip(), department.name))
        return personEx
