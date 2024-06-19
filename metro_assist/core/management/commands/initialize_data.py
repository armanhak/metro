from django.core.management.base import BaseCommand
from core.models import (PassengerCategory,
                         RequestStatus,
                         RequestMethod,
                         Uchastok, Smena, Rank,
                         WorkTime, Gender
                         )

class Command(BaseCommand):
    help = 'Initialize data for PassengerCategory, RequestStatus, and RequestMethod'

    def handle(self, *args, **kwargs):
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

        request_methods = [
            {'method': 'Телефон'},
            {'method': 'Электронные сервисы'},
        ]

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

        smenas = [
            {'name': '1', 'description': ''},
            {'name': '2', 'description': ''},
            {'name': '1(Н)', 'description': ''},
            {'name': '2(Н)', 'description': ''},
            {'name': '5', 'description': ''},
        ]

        ranks = [
            {'name': 'ЦСИ', 'description': ''},
            {'name': 'ЦИО', 'description': ''},
            {'name': 'ЦИ', 'description': ''},
        ]
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

        for category in passenger_categories:
            PassengerCategory.objects.get_or_create(code=category['code'], defaults={'description': category['description']})

        for status in request_statuses:
            RequestStatus.objects.get_or_create(status=status['status'])

        for method in request_methods:
            RequestMethod.objects.get_or_create(method=method['method'])

        for uchastok in uchastoks:
            Uchastok.objects.get_or_create(name=uchastok['name'], defaults={'description': uchastok['description']})
        genders = [
            {'name': 'Мужской'},
            {'name': 'Женский'},
        ]
        for smena in smenas:
            Smena.objects.get_or_create(name=smena['name'], defaults={'description': smena['description']})

        for gender in genders:
            Gender.objects.get_or_create(name=gender['name'])

        for rank in ranks:
            Rank.objects.get_or_create(name=rank['name'], defaults={'description': rank['description']})            
        for wt in work_times:
            uchastok = Uchastok.objects.get(name=wt['uchastok_name'])
            WorkTime.objects.get_or_create(
                uchastok=uchastok,
                start_time=wt['start_time'],
                end_time=wt['end_time']
            )
        self.stdout.write(self.style.SUCCESS('Data initialized successfully'))
