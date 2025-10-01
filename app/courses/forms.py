from django import forms
from courses.models import Purchase, CoursePackage
from accounts.models import Student
from courses.models import CoursePackage

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['student', 'package', 'hours_added', 'amount_paid']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'package': forms.HiddenInput(),
            'hours_added': forms.NumberInput(attrs={'min': 1}),
            'amount_paid': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        package = kwargs.pop('package', None)
        super().__init__(*args, **kwargs)
        
        if package:
            self.fields['package'].initial = package.id
            self.fields['hours_added'].initial = package.hours
            self.fields['amount_paid'].initial = package.price

class CoursePackageForm(forms.ModelForm):
    class Meta:
        model = CoursePackage
        fields = ['name', 'hours', 'price', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'hours': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md', 'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md', 'rows': '3'}),
        }
        labels = {
            'name': 'Nom du forfait',
            'hours': 'Nombre d\'heures',
            'price': 'Prix (€)',
            'description': 'Description',
        }