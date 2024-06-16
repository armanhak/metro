from django.core.management.base import BaseCommand
from core.models import PassengerCategory, RequestStatus, RequestMethod

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

        for category in passenger_categories:
            PassengerCategory.objects.get_or_create(code=category['code'], defaults={'description': category['description']})

        for status in request_statuses:
            RequestStatus.objects.get_or_create(status=status['status'])

        for method in request_methods:
            RequestMethod.objects.get_or_create(method=method['method'])

        self.stdout.write(self.style.SUCCESS('Data initialized successfully'))
