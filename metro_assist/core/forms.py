from django import forms
from .models import Passenger, Request, Employee

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = '__all__'
        widgets = {
            # 'name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            # 'additional_phone_info': forms.Textarea(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            # 'smena': forms.Select(attrs={'class': 'form-control'}),
            # 'uchastok': forms.Select(attrs={'class': 'form-control'}),

            # 'additional_info': forms.Textarea(attrs={'class': 'form-control'}),
            # 'has_eks': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
        # widgets = {
        #     'category': forms.Select(choices=Passenger.CATEGORY_CHOICES),
        # }

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        # widgets = {
        #     # 'name': forms.TextInput(attrs={'class': 'form-control'}),
        #     # 'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        #     # 'additional_phone_info': forms.Textarea(attrs={'class': 'form-control'}),
        #     'gender': forms.Select(attrs={'class': 'form-control'}),
        #     'smena': forms.Select(attrs={'class': 'form-control'}),
        #     # 'rank': forms.Select(attrs={'class': 'form-control'}),
        #     # 'category': forms.Select(attrs={'class': 'form-control'}),
        #     # 'additional_info': forms.Textarea(attrs={'class': 'form-control'}),
        #     # 'has_eks': forms.CheckboxInput(attrs={'class': 'form-control'}),
        # }