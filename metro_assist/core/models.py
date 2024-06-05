from django.db import models
from django.contrib.auth.models import User

# Модель для пассажиров
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

    def __str__(self):
        return self.name
# Модель для станций метро
class MetroStation(models.Model):
    name_station = models.CharField(max_length=255)
    name_line = models.CharField(max_length=255)
    id_line = models.IntegerField()

    def __str__(self):
        return self.name_station

# Модель для времени между станциями
class MetroTravelTime(models.Model):
    id_st1 = models.ForeignKey(MetroStation, related_name='start_station', on_delete=models.CASCADE)
    id_st2 = models.ForeignKey(MetroStation, related_name='end_station', on_delete=models.CASCADE)
    time = models.FloatField()  # Время в минутах

    def __str__(self):
        return f"{self.id_st1} to {self.id_st2}"

# Модель для времени пересадки между станциями
class MetroTransferTime(models.Model):
    id1 = models.ForeignKey(MetroStation, related_name='transfer_start_station', on_delete=models.CASCADE)
    id2 = models.ForeignKey(MetroStation, related_name='transfer_end_station', on_delete=models.CASCADE)
    time = models.FloatField()  # Время в минутах

    def __str__(self):
        return f"Transfer from {self.id1} to {self.id2}"

# Модель для сотрудников
class Employee(models.Model):
    date = models.DateField()
    time_work = models.CharField(max_length=50)
    fio = models.CharField(max_length=255)
    uchastok = models.CharField(max_length=50)
    smena = models.CharField(max_length=50)
    rank = models.CharField(max_length=50)
    sex = models.CharField(max_length=1)  # 'M' or 'F'

    def __str__(self):
        return self.fio

# Модель для заявок
class Request(models.Model):
    id_pas = models.ForeignKey('Passenger', on_delete=models.CASCADE)
    
    datetime = models.DateTimeField()
    time3 = models.TimeField()
    time4 = models.TimeField()
    cat_pas = models.CharField(max_length=3, choices=Passenger.CATEGORY_CHOICES)
    status = models.CharField(max_length=50)
    tpz = models.DateTimeField()
    insp_sex_m = models.IntegerField()
    insp_sex_f = models.IntegerField()
    time_over = models.TimeField()  # Время в формате HH:MM:SS
    id_st1 = models.ForeignKey(MetroStation, related_name='request_start_station', on_delete=models.CASCADE)
    id_st2 = models.ForeignKey(MetroStation, related_name='request_end_station', on_delete=models.CASCADE)

    def __str__(self):
        return f"Request {self.id_request}"

# Модель для отмен заявок
class RequestCancellation(models.Model):
    id_bid = models.ForeignKey(Request, on_delete=models.CASCADE)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"Cancellation {self.id_bid}"

# Модель для переноса заявок
class RequestReschedule(models.Model):
    id_bid = models.ForeignKey(Request, on_delete=models.CASCADE)
    time_edit = models.DateTimeField()
    time_s = models.DateTimeField()
    time_f = models.DateTimeField()

    def __str__(self):
        return f"Reschedule {self.id_bid}"

# Модель для неявки пассажира
class NoShow(models.Model):
    id_bid = models.ForeignKey(Request, on_delete=models.CASCADE)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"No Show {self.id_bid}"

