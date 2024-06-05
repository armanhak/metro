# core/views.py
from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Passenger, Request, Employee #WorkSchedule
from .serializers import PassengerSerializer, RequestSerializer, EmployeeSerializer#, WorkScheduleSerializer
from .forms import PassengerForm, RequestForm, EmployeeForm

# ViewSet'ы для API
class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

# class WorkScheduleViewSet(viewsets.ModelViewSet):
#     queryset = WorkSchedule.objects.all()
#     serializer_class = WorkScheduleSerializer

# Обработчики для регистрации пассажира, заявки и сотрудника
def register_passenger(request):
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = PassengerForm()
    return render(request, 'register_passenger.html', {'form': form})

def register_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = RequestForm()
    passengers = Passenger.objects.all()
    return render(request, 'register_request.html', {'form': form, 'passengers': passengers})

def register_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = EmployeeForm()
    return render(request, 'register_employee.html', {'form': form})

# Представление для главной страницы
def index(request):
    requests = Request.objects.all()
    if not requests.exists():
        requests = None
    return render(request, 'index.html', {'requests': requests})