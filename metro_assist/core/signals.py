from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Request, TimeMatrix
import networkx as nx
from datetime import datetime, timedelta
from .views import metro_graph
from .utils import TaskManager, make_aware_if_naive, time_to_seconds


# Функция для расчета времени между заявками
def calculate_time_into_tasks(task1, task2, date=None):
    
    # Функция для проверки и приведения к "aware" datetime
    
    travel_time = metro_graph.get_travel_time(int(task1.id_st2_id), 
                                              int(task2.id_st1_id))
    if isinstance(task1.datetime, str):
        task1_start = make_aware_if_naive(datetime.strptime(task1.datetime, '%Y-%m-%dT%H:%M'))
    else:
        task1_start = make_aware_if_naive(task1.datetime)

    if isinstance(task2.datetime, str):
        task2_start = make_aware_if_naive(datetime.strptime(task2.datetime, '%Y-%m-%dT%H:%M'))
    else:
        task2_start = make_aware_if_naive(task2.datetime)

    if isinstance(task1.time_over, str):
        task1_time_over = datetime.strptime(task1.time_over, "%H:%M:%S").time()
    else:
        task1_time_over = task1.time_over



    task1_end = task1_start + timedelta(hours=task1_time_over.hour,
                                            minutes=task1_time_over.minute,
                                            seconds=task1_time_over.second)
    if task1_end > task2_start - timedelta(minutes = 15):
        return 60000
    
    # print('travel_time', travel_time, 
    #       'task en t+trtime', 
    #       task1_end + timedelta(seconds = travel_time), 
    #       'task2 st',task2_start, 
    #       'tsk2_st-15',task2_start-timedelta(minutes = 15) )
    
    if task1_end + timedelta(seconds = travel_time) <= task2_start - timedelta(minutes = 15):
        task1_task2_time = travel_time + time_to_seconds(task1_time_over)
    else:
        return 60000
    
    return task1_task2_time

@receiver(post_save, sender=Request)
def update_time_matrix(sender, instance, created, **kwargs):
    exclude_statuses = ['Отмена', 'Отказ', 'Отмена заявки по просьбе пассажира', 
                        'Отмена заявки по неявке пассажира',
                        'Отказ по регламенту'
                        ]
    print(f"Сигнал сработал для Request ID: {instance.id}")

    if isinstance(instance.datetime, str):
        
        date = datetime.strptime(instance.datetime, '%Y-%m-%dT%H:%M').date()

    else:
        date  = str(instance.datetime.date())
    date  = str(date)
    task_manager = TaskManager(date)
    
    
    # if created:
    requests = Request.objects.filter(datetime__date=date).exclude(status__status__in=exclude_statuses)
    for request in requests:
        if request != instance:

            t12 = calculate_time_into_tasks(instance, request)
            t21 = calculate_time_into_tasks(request, instance)

            if t12!=60000:
                TimeMatrix.objects.update_or_create(id1=instance, id2=request, defaults={'time': t12})
            if t21!=60000:
                TimeMatrix.objects.update_or_createate(id1=request, id2=instance, defaults={'time': t21})

@receiver(pre_delete, sender=Request)
def delete_time_matrix(sender, instance, **kwargs):
    print('del work')

    TimeMatrix.objects.filter(id1=instance).delete()
    TimeMatrix.objects.filter(id2=instance).delete()