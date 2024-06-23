from django.core.management.base import BaseCommand
import os 
import json
from django.conf import settings
from tqdm import tqdm
from core.models import (PassengerCategory,
                         RequestStatus,
                         RequestMethod,
                         Uchastok, Smena, Rank,
                         WorkTime, Gender,
                         MetroStation, MetroTravelTime, 
                         MetroTransferTime,
                         )

class Command(BaseCommand):
    help = 'Initialize data for PassengerCategory, RequestStatus, and RequestMethod'

    def load_metro_stations(self):
        file_path = os.path.join(settings.BASE_DIR,'base_data', 'Наименование станций метро.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print("Loading metro_stations...")
        for item in tqdm(data):
            station, created = MetroStation.objects.update_or_create(
                id= item['id'],
                defaults={
                    'name_station': item['name_station'],
                    'name_line': item['name_line'],
                    'id_line': item['id_line']
                }
            )
            # if created:
            #     self.stdout.write(self.style.SUCCESS(f'Metro station {station.name_station} created'))
            # else:
            #     self.stdout.write(self.style.SUCCESS(f'Metro station {station.name_station} updated'))
        self.stdout.write(self.style.SUCCESS(f'Metro stations created'))

    def load_metro_travel_times(self):
        file_path = os.path.join(settings.BASE_DIR, 'base_data', 'Метро время между станциями.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print("Loading mero_travel_times...")
        for item in tqdm(data):
            station1 = MetroStation.objects.get(id=item['id_st1'])
            station2 = MetroStation.objects.get(id=item['id_st2'])
            travel_time, created = MetroTravelTime.objects.update_or_create(
                id_st1=station1,
                id_st2=station2,
                defaults={
                    'time': float(item['time'].replace(',', '.'))
                }
            )
            # if created:
            #     self.stdout.write(self.style.SUCCESS(f'Travel time from {station1.name_station} to {station2.name_station} created'))
            # else:
            #     self.stdout.write(self.style.SUCCESS(f'Travel time from {station1.name_station} to {station2.name_station} updated'))
        self.stdout.write(self.style.SUCCESS(f'Travel times created'))

    def load_metro_transfer_times(self):
        file_path = os.path.join(settings.BASE_DIR, 'base_data', 'Метро время пересадки между станциями.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print("Loading metro_transfer_times...")
        for item in tqdm(data):
            station1 = MetroStation.objects.get(id=item['id1'])
            station2 = MetroStation.objects.get(id=item['id2'])
            transfer_time, created = MetroTransferTime.objects.update_or_create(
                id1=station1,
                id2=station2,
                defaults={
                    'time': float(item['time'].replace(',', '.'))
                }
            )
            # if created:
            #     self.stdout.write(self.style.SUCCESS(f'Transfer time from {station1.name_station} to {station2.name_station} created'))
            # else:
            #     self.stdout.write(self.style.SUCCESS(f'Transfer time from {station1.name_station} to {station2.name_station} updated'))
        self.stdout.write(self.style.SUCCESS(f'Transfer times created'))

    def load_passenger_categories(self):
        passenger_categories = [
            {"code": "ИЗТ", "description": "Инвалид по зрению (тотальный, сопровождение по метрополитену)"},
            {"code": "ИЗ", "description": "Инвалид по зрению с остаточным зрением (слабовидящий, сопровождение по метрополитену)"},
            {"code": "ИС", "description": "Инвалид по слуху (в основном помощь в ориентировании)"},
            {"code": "ИК", "description": "Инвалид колясочник (передвижение в инвалидной коляске)"},
            {"code": "ИО", "description": "Инвалид опорник (необходима поддержка при передвижениии/или на лестницах/эскалаторах)"},
            {"code": "ДИ", "description": "Ребенок инвалид (зачастую передвижение в инвалидной коляске)"},
            {"code": "ПЛ", "description": "Пожилой человек (необходима поддержка при передвижении и/или на лестницах/эскалаторах)"},
            {"code": "РД", "description": "Родители с детьми (сопровождение ребенка)"},
            {"code": "РДК", "description": "Родители с детскими колясками (помощь с детской коляской)"},
            {"code": "ОГД", "description": "Организованные группы детей (сопровождение по метрополитену)"},
            {"code": "ОВ", "description": "Временно маломобильные (после операции, переломы и прочее)"},
            {"code": "ИУ", "description": "Люди с ментальной инвалидностью"}
        ]    
        for category in passenger_categories:
            PassengerCategory.objects.get_or_create(code=category['code'], 
                                                    defaults={'description': category['description']})    
    def load_request_stauses(self):
        request_statuses = [
            {'status': 'В рассмотрении'},
            {'status': 'Принята'},
            {'status': 'Инспектор выехал'},
            {'status': 'Инспектор на месте'},
            {'status': 'Поездка'},
            {'status': 'Заявка закончена'},
            {'status': 'Выявление'},
            {'status': 'Лист Ожидания'},
            {'status': 'Отмена'}, 
            {'status':'Отказ'}, 
            {'status': 'Пассажир опаздывает'},
            {'status': 'Инспектор опаздывает'},
            {'status': 'Не подтверждена'}
        ]
        for status in request_statuses:
            RequestStatus.objects.get_or_create(status=status['status'])
    def load_request_methods(self):
        request_methods = [
            {'method': 'Телефон'},
            {'method': 'Электронные сервисы'},
        ]
        for method in request_methods:
            RequestMethod.objects.get_or_create(method=method['method'])
    def load_uchasotk(self):
        uchastoks = [
            {'name': 'ЦУ-1', 'description': ''},
            {'name': 'ЦУ-2', 'description': ''},
            {'name': 'ЦУ-3', 'description': ''},
            {'name': 'ЦУ-3(Н)', 'description': ''},
            {'name': 'ЦУ-4', 'description': ''},
            {'name': 'ЦУ-4(Н)', 'description': ''},
            {'name': 'ЦУ-5', 'description': ''},
            {'name': 'ЦУ-8', 'description': ''},
        ]
        for uchastok in uchastoks:
            Uchastok.objects.get_or_create(name=uchastok['name'], 
                                           defaults={'description': uchastok['description']})
    def load_smens(self):
        smenas = [
            {'name': '1', 'description': ''},
            {'name': '2', 'description': ''},
            {'name': '1(Н)', 'description': ''},
            {'name': '2(Н)', 'description': ''},
            {'name': '5', 'description': ''},
        ]
        for smena in smenas:
            Smena.objects.get_or_create(name=smena['name'],
                                         defaults={'description': smena['description']})
    def load_ranks(self):
        ranks = [
            {'name': 'ЦСИ', 'description': ''},
            {'name': 'ЦИО', 'description': ''},
            {'name': 'ЦИ', 'description': ''},
        ]
        for rank in ranks:
            Rank.objects.get_or_create(name=rank['name'], 
                                       defaults={'description': rank['description']})  
    def load_genders(self):    
        genders = [
            {'name': 'Мужской'},
            {'name': 'Женский'},
        ]
        for gender in genders:
            Gender.objects.get_or_create(name=gender['name'])

    def load_work_times(self):
        work_times = [
            {'uchastok_name': 'ЦУ-1', 'start_time': '07:00', 'end_time': '19:00'},
            {'uchastok_name': 'ЦУ-1', 'start_time': '08:00', 'end_time': '20:00'},
            {'uchastok_name': 'ЦУ-2', 'start_time': '07:00', 'end_time': '19:00'},
            {'uchastok_name': 'ЦУ-2', 'start_time': '08:00', 'end_time': '20:00'},
            {'uchastok_name': 'ЦУ-3', 'start_time': '07:00', 'end_time': '19:00'},
            {'uchastok_name': 'ЦУ-3', 'start_time': '08:00', 'end_time': '20:00'},
            {'uchastok_name': 'ЦУ-3', 'start_time': '10:00', 'end_time': '22:00'},
            {'uchastok_name': 'ЦУ-3(Н)', 'start_time': '20:00', 'end_time': '08:00'},
            {'uchastok_name': 'ЦУ-4', 'start_time': '07:00', 'end_time': '19:00'},
            {'uchastok_name': 'ЦУ-4', 'start_time': '08:00', 'end_time': '20:00'},
            {'uchastok_name': 'ЦУ-4', 'start_time': '10:00', 'end_time': '22:00'},
            {'uchastok_name': 'ЦУ-4(Н)', 'start_time': '20:00', 'end_time': '08:00'},
            {'uchastok_name': 'ЦУ-5', 'start_time': '07:00', 'end_time': '19:00'},
            {'uchastok_name': 'ЦУ-5', 'start_time': '08:00', 'end_time': '20:00'},
            {'uchastok_name': 'ЦУ-5', 'start_time': '10:00', 'end_time': '22:00'},
            {'uchastok_name': 'ЦУ-8', 'start_time': '07:00', 'end_time': '19:00'},
            {'uchastok_name': 'ЦУ-8', 'start_time': '08:00', 'end_time': '20:00'},
        ]
        for wt in work_times:
            uchastok = Uchastok.objects.get(name=wt['uchastok_name'])
            WorkTime.objects.get_or_create(
                uchastok=uchastok,
                start_time=wt['start_time'],
                end_time=wt['end_time']
            )


    def handle(self,  *args, **kwargs):
        
        self.load_metro_stations()
        self.load_metro_travel_times()
        self.load_metro_transfer_times()

        self.load_passenger_categories()
        self.load_request_stauses()
        self.load_request_methods()
        self.load_uchasotk()
        self.load_smens()
        self.load_ranks()
        self.load_ranks()
        self.load_genders()
        self.load_work_times()

        self.stdout.write(self.style.SUCCESS('Data initialized successfully'))

