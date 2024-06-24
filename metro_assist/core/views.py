# core/views.py
from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import (Passenger, Request, Employee, 
                     MetroStation, RequestMethod, 
                     RequestStatus, PassengerCategory,
                      Uchastok, Smena, Rank, WorkTime, Gender,
                     TimeMatrix, EmployeeSchedule
                     ) #WorkSchedule
from .serializers import PassengerSerializer, RequestSerializer, EmployeeSerializer#, WorkScheduleSerializer
from .forms import PassengerForm, RequestForm, EmployeeForm
from datetime import time
from django.http import JsonResponse, HttpResponse
from .utils import (MetroGraph, convert_seconds_to_hms, 
                    combine_date_time_to_min_since_noon_yesterday, 
                    add_lunch, to_minutes_since_noon_yesterday,
                      time_to_min)
import networkx as nx
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from .vrptw import MetroVRPSolver, convert_to_time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import os
from django.conf import settings


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
        work_time_id = request.POST['work_time']
        start_work_date = request.POST['start_work_date']
        # start_work_date = datetime.strptime(start_work_date, '%d.%m.%Y').date()

        work_time = WorkTime.objects.get(id=work_time_id)

        employee = Employee.objects.create(
            first_name=first_name,
            last_name=last_name,
            patronymic = patronymic,
            initials = initials,
            gender=gender,
            rank=rank,
            work_time = work_time,
            # smena=smena,
            # uchastok=uchastok,
            work_phone=work_phone,
            personal_phone=personal_phone,
            tab_number=tab_number,
            light_duty=light_duty
        )
        employe_scheld = EmployeeSchedule.objects.create(
            start_work_date = start_work_date,
            employee = employee,
            smena = smena
            )





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

    exclude_statuses = ['Отмена', 'Отказ', 'Отмена заявки по просьбе пассажира', 
                        'Отмена заявки по неявке пассажира',
                        'Отказ по регламенту'
                        ]
    
    if request.method == 'POST':
        metro_id_name_dict = MetroStation.objects.all().values('id', 'name_station')
        metro_id_name_dict = {station['id']: station['name_station'] for station in metro_id_name_dict}

        date_str = request.POST.get('distribution_date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        task_zero_date_time = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(hours=12)

        previous_date = date - timedelta(days=1)
        start_times_previous_day = [time(19, 0), time(20, 0)]

        requests = Request.objects.filter(datetime__date=date).exclude(status__status__in=exclude_statuses)
        if not requests.exists():
            return render(request, 'request_distribution.html', {'message':f'Не нашлись заявки на {date_str}'})

        employers_schedule = EmployeeSchedule.objects.filter(
                            Q(start_work_date=date) |
                            Q(start_work_date=previous_date, 
                              employee__work_time__start_time__in=start_times_previous_day)
                        )
        if not employers_schedule.exists():
            return render(request, 'request_distribution.html', {'message':'Не нашлись сотрудники на эту дату'})



        # employees = [{"DATE":schedule.start_work_date, 
        #               "start":schedule.employee.work_time.start_time,
        #               "end": schedule.employee.work_time.end_time,
        #               "ID": schedule.employee.id } for schedule in employers_schedule if schedule.start_work_date==previous_date]
        # employees = [{"ID":e.id,"sex":e.gender.name, "FIO":e.initials} for e in employees]


        def fetch_employers(qsschedule_set):
            emp_list = [
                {
                    "ID": schedule.employee.id,
                    "FIO": schedule.employee.initials,
                    "SEX": schedule.employee.gender.name,
                    "DATE": schedule.start_work_date,
                    "start":schedule.employee.work_time.start_time,
                    "end": schedule.employee.work_time.end_time,
                    "smena":schedule.smena.name

                }
                for schedule in qsschedule_set
                ]
            
            for emp in emp_list:
                emp['start'] = combine_date_time_to_min_since_noon_yesterday(task_zero_date_time, emp['DATE'], emp['start'])
                if emp["DATE"]==date and emp['smena'] in ['1Н', '2Н']:
                    emp['end'] = combine_date_time_to_min_since_noon_yesterday(task_zero_date_time, date + timedelta(days=1),  emp['end'])
                else:
                    emp['end'] = combine_date_time_to_min_since_noon_yesterday(task_zero_date_time, date,  emp['end'])

            
            return emp_list
        
        def fetch_task(tasks):
            for i in range(len(tasks)):
                tasks[i]['start'] = to_minutes_since_noon_yesterday(task_zero_date_time , tasks[i]['datetime'])
                tasks[i]['end'] = tasks[i]['start'] + time_to_min(tasks[i]['time_over'])
                # print(tasks[i]['start'] )
            return tasks
        # Получение всех записей TimeMatrix, которые соответствуют полученным Request ID
        employees_m = fetch_employers(employers_schedule.filter(employee__gender=1))
        employees_f = fetch_employers(employers_schedule.filter(employee__gender=2))

        tasksm = requests.filter(insp_sex_m__gt=0)
        tasksf = requests.filter(insp_sex_f__gt=0)

        task_m_ids = tasksm.values_list('id', flat=True)
        task_f_ids = tasksf.values_list('id', flat=True)

        timematrix_entries_m = TimeMatrix.objects.filter(id1__in=task_m_ids, id2__in=task_m_ids)
        timematrix_entries_f = TimeMatrix.objects.filter(id1__in=task_f_ids, id2__in=task_f_ids)

        # Преобразование TimeMatrix в нужный формат
        task_time_matrix_m = {f'{entry.id1_id}-{entry.id2_id}': entry.time for entry in timematrix_entries_m}
        task_time_matrix_f = {f'{entry.id1_id}-{entry.id2_id}': entry.time for entry in timematrix_entries_f}
        tasksf = fetch_task(list(tasksf.values()))
        tasksm = fetch_task(list(tasksm.values()))
        try:     
            solvers = [] 
            if (len(tasksf)>0) & (len(employees_f)> 0):
                solver_female = MetroVRPSolver(
                        task_date=date_str,
                        workers=employees_f,
                        tasks=tasksf,
                        task_time_matrix_dict = task_time_matrix_f,
                        G = metro_graph.G,
                        task_sex='f'
                    )    
                solvers.append(solver_female)   

            if (len(tasksm)>0) & (len(employees_m)>0):

                solver_male = MetroVRPSolver(
                        task_date=date_str,
                        workers=employees_m,
                        tasks=tasksm,
                        task_time_matrix_dict = task_time_matrix_m,
                        G = metro_graph.G,
                        task_sex='m'
                    )
                solvers.append(solver_male) 
        
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(solver.run) for solver in solvers]
                results = [f.result() for f in as_completed(futures)]

            results = pd.concat(results, axis=0, ignore_index=True)
            for col in [
                        'Начало рабочего дня', 
                        'Конец рабочего дня', 
                        'Начальное время выполнения',
                        'Конечное время выполнения',
                        # 'Продолжительность'
                        ]:
                results[col] = results[col].map(convert_to_time)

            results = add_lunch(results)# добавим время обеда

            stat = results[['Сотрудник', 'Пол', 'Продолжительность']].groupby(['Сотрудник', 'Пол'])\
                [ 'Продолжительность'].agg(['count', 'mean', 'sum', 'min', 'max']).reset_index()
            stat = stat.rename(columns = {'count': 'Кол-во заявок', 
                                          'mean':'Средняя продолжительность времени на одну заявку (мин)',
                                          'sum':"Суммарное время выполнения всех заявок (мин)",
                                          'min':'Минимальное потраченное время на заявку (мин)',
                                          'max':'Максимальное потраченное время на заявку (мин)',
                                          })
            stat.to_excel('stat.xlsx', index=False)# Сохраним статистику по времени выполнению задач

            results['Продолжительность']-=720 #12 часов, начало отсчета предыдущего дня
            results['Продолжительность'] = results['Продолжительность'].map(convert_to_time)

            for col in ['Начальная станция', 'Конечная станция']:
                results[col] = results[col].replace(metro_id_name_dict)
            # results.to_excel('a.xlsx', index=False)
            file_path = generate_results_file(results, 'results')
            stat_path = generate_results_file(stat.reset_index(drop=True), 'stat')
            
            # Присваиваем путь к файлу в сессии, чтобы позже можно было его скачать
            request.session['results_file_path'] = file_path
            request.session['stat_file_path'] = stat_path
            table_html = results.to_html(index=False, classes='table table-striped')

            return render(request, 'request_distribution.html', {
                'distribution_date': date_str,
                'results_table': table_html, 
                'message':''
            })
        except Exception as e:
             return render(request, 'request_distribution.html', {

                'message':f'Не удалось распределить {e}'
            })           

    return render(request, 'request_distribution.html', {'message':''})

def generate_results_file(results, name):
    file_path = os.path.join(settings.BASE_DIR, name, f'{name}.xlsx')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    results.to_excel(file_path, index=False)
    return file_path
def download_results(request):
    file_path = request.session.get('results_file_path')
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    return redirect('distribute_requests')
def download_stat(request):
    file_path = request.session.get('stat_file_path')
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    return redirect('distribute_requests')
