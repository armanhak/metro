import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Employee, MetroStation, MetroTravelTime, MetroTransferTime, Request, Passenger, RequestReschedule, RequestCancellation, NoShow
from datetime import datetime
import pytz

class Command(BaseCommand):
    help = 'Load data from JSON file into the database'

    def parse_datetime(self, date_str):
        formats = ['%d.%m.%Y %H:%M:%S',
                   '%Y-%m-%d %H:%M:%S', 
                   '%d.%m.%Y %H:%M','%Y-%m-%d %H:%M',]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return pytz.timezone(settings.TIME_ZONE).localize(dt)
            except ValueError:
                continue
        raise ValueError(f"time data '{date_str}' does not match any known formats")

    def parse_time(self, time_str):
        formats = ['%H:%M:%S', '%H:%M']
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt).time()
            except ValueError:
                continue
        raise ValueError(f"time data '{time_str}' does not match any known formats")

    def load_employees(self):
        file_path = os.path.join(settings.BASE_DIR,'base_data',  'Сотрудники.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                employee, created = Employee.objects.update_or_create(
                    id= item['ID'],
                    defaults={
                        
                        'date': datetime.strptime(item['DATE'], '%d.%m.%Y').date(),
                        'time_work': item['TIME_WORK'],
                        'fio': item['FIO'],
                        'uchastok': item['UCHASTOK'],
                        'smena': item['SMENA'],
                        'rank': item['RANK'],
                        'sex': item['SEX'][0],  # 'Мужской' -> 'М', 'Женский' -> 'Ж'
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Employee {employee.fio} created'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Employee {employee.fio} updated'))

    def load_metro_stations(self):
        file_path = os.path.join(settings.BASE_DIR,'base_data', 'Наименование станций метро.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                station, created = MetroStation.objects.update_or_create(
                    id= item['id'],
                    defaults={
                        'name_station': item['name_station'],
                        'name_line': item['name_line'],
                        'id_line': item['id_line']
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Metro station {station.name_station} created'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Metro station {station.name_station} updated'))

    def load_metro_travel_times(self):
        file_path = os.path.join(settings.BASE_DIR, 'base_data', 'Метро время между станциями.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                station1 = MetroStation.objects.get(id=item['id_st1'])
                station2 = MetroStation.objects.get(id=item['id_st2'])
                travel_time, created = MetroTravelTime.objects.update_or_create(
                    id_st1=station1,
                    id_st2=station2,
                    defaults={
                        'time': float(item['time'].replace(',', '.'))
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Travel time from {station1.name_station} to {station2.name_station} created'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Travel time from {station1.name_station} to {station2.name_station} updated'))

    def load_metro_transfer_times(self):
        file_path = os.path.join(settings.BASE_DIR, 'base_data', 'Метро время пересадки между станциями.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                station1 = MetroStation.objects.get(id=item['id1'])
                station2 = MetroStation.objects.get(id=item['id2'])
                transfer_time, created = MetroTransferTime.objects.update_or_create(
                    id1=station1,
                    id2=station2,
                    defaults={
                        'time': float(item['time'].replace(',', '.'))
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Transfer time from {station1.name_station} to {station2.name_station} created'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Transfer time from {station1.name_station} to {station2.name_station} updated'))

    def load_requests(self):
        file_path = os.path.join(settings.BASE_DIR, 'base_data', 'Заявки.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                # passenger = Passenger.objects.get(id=item['id_pas']) 
                # passenger = item['id_pas']
                try:
                    passenger = Passenger.objects.get(id=item['id_pas'])
                except Passenger.DoesNotExist:
                    passenger = Passenger.objects.create(
                        id=item['id_pas'],
                        name="Тестовый Пассажир",
                        contact_phone="0000000000",
                        gender="Не указан",
                        category="IU",
                        additional_info="Тестовый пассажир создан автоматически",
                        has_eks=False
                    )
                station1 = MetroStation.objects.get(id=item['id_st1'])
                station2 = MetroStation.objects.get(id=item['id_st2'])
                request, created = Request.objects.update_or_create(
                    id=item['id'],

                    defaults={
                        'id_pas': passenger,
                        'datetime': self.parse_datetime(item['datetime']),#datetime.strptime(item['datetime'], '%d.%m.%Y %H:%M:%S'),
                        'time3': datetime.strptime(item['time3'], '%H:%M:%S').time(),
                        'time4': datetime.strptime(item['time4'], '%H:%M:%S').time(),
                        'cat_pas': item['cat_pas'],
                        'status': item['status'],
                        'tpz': self.parse_datetime(item['tpz']),#datetime.strptime(item['tpz'], '%d.%m.%Y %H:%M:%S'),
                        'insp_sex_m': int(item['INSP_SEX_M']),
                        'insp_sex_f': int(item['INSP_SEX_F']),
                        'time_over': datetime.strptime(item['TIME_OVER'], '%H:%M:%S').time(),
                        'id_st1': station1,
                        'id_st2': station2,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Request {request.id} created'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Request {request.id} updated'))

    def load_request_reschedules(self):
        file_path = os.path.join(settings.BASE_DIR, 'base_data', 'Переносы заявок по времени.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                try:
                    request = Request.objects.get(id=item['id_bid'])
                    reschedule, created = RequestReschedule.objects.update_or_create(
                        id_bid=request,
                        defaults={
                            'time_edit': self.parse_datetime(item['time_edit']),
                            'time_s': self.parse_time(item['time_s']),
                            'time_f': self.parse_time(item['time_f']),
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'RequestReschedule {reschedule.id_bid.id} created'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'RequestReschedule {reschedule.id_bid.id} updated'))
                except Exception as e:
                    self.stdout.write(self.style.SUCCESS(f'RequestReschedule {item["id_bid"]} dont add'))



    def load_request_cancellations(self):
        file_path = os.path.join(settings.BASE_DIR, 'base_data', 'Отмены заявок.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                request = Request.objects.get(id=item['ID_BID'])
                cancellation, created = RequestCancellation.objects.update_or_create(
                    id_bid=request,
                    defaults={
                        'date_time': self.parse_datetime(item['DATE_TIME']),
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'RequestCancellation {cancellation.id_bid.id} created'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'RequestCancellation {cancellation.id_bid.id} updated'))

    def load_no_shows(self):
        file_path = os.path.join(settings.BASE_DIR, 'base_data', 'Неявка пассажира.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                request = Request.objects.get(id=item['ID_BID'])
                no_show, created = NoShow.objects.update_or_create(
                    id_bid=request,
                    defaults={
                        'date_time': self.parse_datetime(item['DATE_TIME']),
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'NoShow {no_show.id_bid.id} created'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'NoShow {no_show.id_bid.id} updated'))


    def handle(self, *args, **kwargs):
        self.load_employees()
        self.load_metro_stations()
        self.load_metro_travel_times()
        self.load_metro_transfer_times()
        self.load_requests()     
        self.load_request_reschedules()
        self.load_request_cancellations()
        self.load_no_shows()        