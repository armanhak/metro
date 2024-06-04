from django import forms
from .models import Passenger, Request, Employee

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = '__all__'
        widgets = {
            'category': forms.Select(choices=Passenger.CATEGORY_CHOICES),
        }

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'