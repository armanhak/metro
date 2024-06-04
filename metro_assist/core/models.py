from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class Passenger(models.Model):
    CATEGORY_CHOICES = [
        ('IZT', '(ИЗТ) Инвалид по зрению (тотальный)'),
        ('IZ', '(ИЗ) Инвалид по зрению с остаточным зрением'),
        ('IS', '(ИС) Инвалид по слуху'),
        ('IK', '(ИК) Инвалид колясочник'),
        ('IO', '(ИО) Инвалид опорник'),
        ('DI', '(ДИ) Ребенок инвалид'),
        ('PL', '(ПЛ) Пожилой человек'),
        ('RD', '(РД) Родители с детьми'),
        ('RDK', '(РДК) Родители с детскими колясками'),
        ('OGD', '(ОГД) Организованные группы детей'),
        ('OV', '(ОВ) Временно маломобильные'),
        ('IU', '(ИУ) Люди с ментальной инвалидностью'),
    ]

    name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES)
    additional_info = models.TextField(null=True, blank=True)
    has_eks = models.BooleanField(default=False)

class Request(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    departure_station = models.CharField(max_length=50)
    arrival_station = models.CharField(max_length=50)
    meeting_point = models.CharField(max_length=255)
    arrival_point = models.CharField(max_length=255)
    request_date = models.DateTimeField()
    method_of_request = models.CharField(max_length=50)
    number_of_passengers = models.IntegerField()
    request_category = models.CharField(max_length=50)
    number_of_employees = models.IntegerField()
    status = models.CharField(max_length=50)
    additional_info = models.TextField(null=True, blank=True)
    assigned_employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    shift = models.CharField(max_length=10)
    position = models.CharField(max_length=50)
    work_phone = models.CharField(max_length=20)
    personal_phone = models.CharField(max_length=20)
    tab_number = models.CharField(max_length=8)
    light_duty = models.BooleanField(default=False)

class WorkSchedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    work_time = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    additional_shift = models.BooleanField(default=False)
    training_date = models.DateField(null=True, blank=True)
    training_end_date = models.DateField(null=True, blank=True)