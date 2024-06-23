# core/views.py
from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import (Passenger, Request, Employee, 
                     MetroStation, RequestMethod, 
                     RequestStatus, PassengerCategory,
                      Uchastok, Smena, Rank, WorkTime, Gender
                     ) #WorkSchedule
from .serializers import PassengerSerializer, RequestSerializer, EmployeeSerializer#, WorkScheduleSerializer
from .forms import PassengerForm, RequestForm, EmployeeForm
from datetime import time
from django.http import JsonResponse
from .utils import MetroGraph, convert_seconds_to_hms
import networkx as nx
from datetime import datetime
from django.utils import timezone
metro_graph = MetroGraph()

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
        # categories = PassengerCategory.objects.all()
        # genders = Gender.objects.all()
    return render(request, 
                  'register_passenger.html',
                    {'form': form, 
                    #  'categories':categories,
                     },)

def register_request(request):
    if request.method == 'POST':
        passenger_id = request.POST['passenger_id']
        # passenger = Passenger.objects.get(id=passenger_id)
        departure_station = request.POST['departure_station_id']
        arrival_station = request.POST['arrival_station_id']
        meeting_point = request.POST['meeting_point']
        arrival_point = request.POST['arrival_point']
        datetime_value = request.POST['datetime']
        method_of_request_id = request.POST['method_of_request']
        request_category_id = request.POST['request_category']
        insp_sex_m = request.POST['insp_sex_m']
        insp_sex_f = request.POST['insp_sex_f']
        status_id = request.POST['status']
        time_over = request.POST['time_over']
        additional_info = request.POST['additional_info']
        print('request_category_id', request_category_id)
        # Задаем значения time3 и time4 программно
        time3 = time(0, 0)  # пример значения, здесь можно задать любые значения времени
        time4 = time(0, 0)  # пример значения, здесь можно задать любые значения времени

        new_request = Request(
            id_pas_id=passenger_id,
            datetime=datetime_value,
            cat_pas_id=request_category_id,
            status_id=status_id,
            insp_sex_m=insp_sex_m,
            insp_sex_f=insp_sex_f,
            time_over=time_over,
            time3=time3,
            time4=time4,
            id_st1_id=departure_station,
            id_st2_id=arrival_station,
            meeting_point=meeting_point,
            arrival_point=arrival_point,
            method_of_request_id=method_of_request_id,
            additional_info=additional_info,
        )
        new_request.save()
        return redirect('/')  # Замените 'success_url' на URL после успешного создания заявки

    passengers = Passenger.objects.all()
    metro_stations = MetroStation.objects.all()
    request_methods = RequestMethod.objects.all()
    request_statuses = RequestStatus.objects.all()
    passenger_categories = PassengerCategory.objects.all()


    
    context = {
        'passengers': passengers,
        'metro_stations': metro_stations,
        'request_methods':request_methods, 
        'request_statuses':request_statuses,
        'passenger_categories': passenger_categories

    }
    print('requests_methods', request_methods)
    return render(request, 'register_request.html', context)


def register_employee(request):
    if request.method == 'POST':
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        patronymic = request.POST['patronymic'].strip()
        initials = f'{last_name} {first_name[0]}.{patronymic[0]}.'
        gender = Gender.objects.get(id=request.POST['gender'])
        smena = Smena.objects.get(id=request.POST['smena'])
        rank = Rank.objects.get(id=request.POST['rank'])
        uchastok = Uchastok.objects.get(id=request.POST['uchastok'])
        work_phone = request.POST['work_phone']
        personal_phone = request.POST['personal_phone']
        tab_number = request.POST['tab_number']
        light_duty = request.POST['light_duty']
        work_times = request.POST.getlist('work_times')

        employee = Employee.objects.create(
            first_name=first_name,
            last_name=last_name,
            patronymic = patronymic,
            initials = initials,
            gender=gender,
            rank=rank,
            smena=smena,
            uchastok=uchastok,
            work_phone=work_phone,
            personal_phone=personal_phone,
            tab_number=tab_number,
            light_duty=light_duty
        )

        for work_time_id in work_times:
            work_time = WorkTime.objects.get(id=work_time_id)
            employee.work_times.add(work_time)

        return redirect('index')

    genders = Gender.objects.all()
    smenas = Smena.objects.all()
    ranks = Rank.objects.filter(name__in=['ЦСИ','ЦИ'])
    uchastoks = Uchastok.objects.all()

    context = {
        'genders': genders,
        'smenas': smenas,
        'ranks': ranks,
        'uchastoks': uchastoks
    }
    return render(request, 'register_employee.html', context)



def get_work_times(request):
    uchastok_id = request.GET.get('uchastok_id')
    work_times = WorkTime.objects.filter(uchastok_id=uchastok_id).values('id', 'start_time', 'end_time')
    return JsonResponse(list(work_times), safe=False)

# Представление для главной страницы
def index(request):
    requests = Request.objects.all()
    if not requests.exists():
        requests = None
    return render(request, 'index.html', {'requests': requests})

def calculate_time_over(request):
    departure = request.GET.get('departure')
    arrival = request.GET.get('arrival')
    # Логика для вычисления времени поездки
    travel_time = get_travel_time(departure, arrival)
    print(travel_time)
    travel_info = get_travel_info(departure, arrival)
    print(travel_info)
    return JsonResponse(travel_info)
    # return JsonResponse({'time_over': travel_time})
def del_req(request):
    id_ = request.GET.get('id')
    print('del', id_)
    req = Request.objects.filter(id=id_).delete()
    return render(request, 'index.html', {'requests': request})

def get_travel_info(departure, arrival):
    global metro_graph
    # Пример логики для вычисления времени поездки между станциями
    # Замените на реальную логику вашего приложения
    try:
        
        (path, travel_time, 
         transfers, transfers_count) = metro_graph.get_path_and_travel_time(
                                                from_station=int(departure), 
                                                to_station=int(arrival), 
                                                weight='weight')

        return {'time_over': convert_seconds_to_hms(travel_time),
                             'travel_path':path,
                             'transfers':transfers, 
                             'transfers_count':transfers_count
                             }
    except nx.NetworkXNoPath:
        return {'time_over': '00:00:00',
                             'travel_path':[],
                             'transfers':[], 
                             'transfers_count':''
                             }
def get_travel_time(departure, arrival):
    global metro_graph
    # Пример логики для вычисления времени поездки между станциями
    # Замените на реальную логику вашего приложения
    try:
        travel_time = metro_graph.get_travel_time(
                                                from_station=int(departure), 
                                                to_station=int(arrival), 
                                                weight='weight'
                                                )
    
        # Конвертируем время в формате HH:MM:SS
        # return int(round(travel_time*60))#sec
        return convert_seconds_to_hms(travel_time)

    except nx.NetworkXNoPath:
        # return 0
        return '00:00:00'
    
    
def request_distribution(request):
    if request.method == 'POST':
        print(request.get('distribution_date'))
    return render(request, 'request_distribution.html')