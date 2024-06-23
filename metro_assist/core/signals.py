from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Request, TimeMatrix
import networkx as nx
from datetime import datetime
# Функция для расчета времени между заявками
def calculate_time(request1, request2):
    # Здесь вы должны реализовать логику для расчета времени между заявками
    # Например, используя граф метро
    G = nx.Graph()  # ваш граф метро
    # используйте данные request1 и request2 для расчета
    time = nx.shortest_path_length(G, source=request1.id_st1.id, target=request2.id_st2.id, weight='weight')
    return time

@receiver(post_save, sender=Request)
def update_time_matrix(sender, instance, created, **kwargs):
    if isinstance(instance.datetime, str):
        date = datetime.strptime(instance.datetime, '%Y-%m-%dT%H:%M').date()
        print('hey', date)
    else:
        date  = instance.datetime.date()

    if created:
        requests = Request.objects.filter(datetime__date=date)
        for request in requests:
            if request != instance:
                time1 = 1#calculate_time(instance, request)
                time2 = 2#calculate_time(request, instance)

                TimeMatrix.objects.create(id1=instance, id2=request, time=time1)
                TimeMatrix.objects.create(id1=request, id2=instance, time=time2)

@receiver(pre_delete, sender=Request)
def delete_time_matrix(sender, instance, **kwargs):
    print('del work')

    TimeMatrix.objects.filter(id1=instance).delete()
    TimeMatrix.objects.filter(id2=instance).delete()