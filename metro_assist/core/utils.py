import networkx as nx
from .models import MetroTravelTime, MetroTransferTime
from itertools import combinations
from datetime import datetime, timedelta
import pandas as pd

def distribute_requests():
    # Основная логика распределения заявок
    pass

def adaptive_distribute_requests():
    # Основная логика адаптивного распределения заявок
    pass

def convert_decimal_minutes_to_seconds(decimal_minutes):
    minutes = int(decimal_minutes)
    seconds = (decimal_minutes - minutes) * 100  # Преобразуем доли минут в секунды
    return minutes * 60 + int(seconds)

def convert_seconds_to_hms(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'

def convert_seconds_to_min(total_seconds):
    # hours, remainder = divmod(total_seconds, 60)
    minutes, seconds = divmod(total_seconds, 60)
    return minutes+ seconds/100

class MetroGraph():
    def __init__(self) -> None:
        self.create_graph()

    def create_graph(self) -> None:
        self.G = nx.Graph()
        travel_data = MetroTravelTime.objects.all()
        transfer_data = MetroTransferTime.objects.all()

        try:
            for entry in travel_data:
                sec = convert_decimal_minutes_to_seconds(entry.time)
                self.G.add_edge(int(entry.id_st1_id), 
                                int(entry.id_st2_id),
                                    weight=sec,
                                    type='travel',
                                    # name_line=entry.id_st1.name_line,
                                    # name_station_from=entry.id_st1.name_station,
                                    # name_station_to=entry.id_st2.name_station

                                    )

            for entry in transfer_data:
                sec = convert_decimal_minutes_to_seconds(entry.time)
                self.G.add_edge(int(entry.id1_id),
                                int(entry.id2_id),
                                weight=sec,
                                type='transfer',
                                # name_line=entry.id_st1.name_line,
                                # name_station_from=entry.id_st1.name_station,
                                # name_station_to=entry.id_st2.name_station
                                )
        except:
            pass
    def check_transfers(self, path):
        "проверка наличия пересадки"
        transfers = []
        for u, v in zip(path[:-1], path[1:]):
            edge_data = self.G.get_edge_data(u, v)
            if edge_data['type'] == 'transfer':
                transfers.append((u, v))
        return transfers
    def get_path_and_travel_time(self, from_station, to_station, weight = 'weight'):
        try:
            path = nx.shortest_path(self.G,
                                    source=from_station,
                                    target=to_station,
                                    weight=weight)
            length = nx.shortest_path_length(self.G,
                                             source=from_station,
                                             target=to_station,
                                             weight=weight)
            transfers = self.check_transfers(path)
            transfers_count = MetroGraph.decline_transfer(len(transfers))
            print('now', path, length, transfers, transfers_count)
            return path, length, transfers, transfers_count
        except nx.NetworkXNoPath:
            return None, 0, None, None
        
    def get_travel_time(self, from_station, to_station, weight = 'weight' ):
        """return seconds from first station to second station"""

        travel_time = nx.shortest_path_length(self.G,                                                  
                                                source=from_station, 
                                                target=to_station,
                                                weight=weight)
        
        
        return travel_time
    @staticmethod
    def decline_transfer(n):
        if n==0:
            return 'Без пересадок'
        if 10 <= n % 100 <= 20:  # Обработка случаев от 11 до 19
            form = "пересадок"
        else:
            last_digit = n % 10
            if last_digit == 1:
                form = "пересадка"
            elif last_digit in [2, 3, 4]:
                form = "пересадки"
            else:
                form = "пересадок"
        
        return f"{n} {form}"
    
def schedule_lunch(schedule, min_lunch_gap=0):
    results = []
    
    def parse_time(time_str):
        return datetime.strptime(time_str, "%H:%M:%S")
    
    def format_time(time):
        return time.strftime("%H:%M:%S")
    
    def is_overlap(interval1, interval2, min_gap=0):
        gap = timedelta(minutes=min_gap)
        return interval1[0] < interval2[1] + gap and interval1[1] + gap > interval2[0]

    def adjust_for_night_shift(start, end):
        """Adjust for night shifts by extending the end time into the next day if necessary."""
        if end <= start:
            end += timedelta(days=1)
        return start, end
    
    def generate_lunch_intervals(lunch_start_min, lunch_end_max, step=30):
        intervals = []
        current_start = lunch_start_min
        while current_start + timedelta(hours=1) <= lunch_end_max:
            intervals.append((current_start, current_start + timedelta(hours=1)))
            current_start += timedelta(minutes=step)
        return intervals

    for employee in schedule:
        employee_id = employee["Сотрудник ID"]
        work_start = parse_time(str(employee["work_start"]))
        work_end = parse_time(str(employee["work_end"]))        
        
        work_start, work_end = adjust_for_night_shift(work_start, work_end)
        
        lunch_start_min = work_start + timedelta(hours=3.5)
        lunch_end_max = work_end - timedelta(hours=1)
        
        requests = employee["requests"]
        time_intervals = [(parse_time(str(start)), parse_time(str(end))) for start, end in requests["time_intervals"]]
        time_intervals = [adjust_for_night_shift(start, end) for start, end in time_intervals]

        possible_lunch_intervals = generate_lunch_intervals(lunch_start_min, lunch_end_max)
        
        lunch_found = False
        for lunch_interval in possible_lunch_intervals:
            if all(not is_overlap(interval, lunch_interval, min_lunch_gap) for interval in time_intervals):
                results.append({
                    "Сотрудник ID": employee_id,
                    "cancelled_request_id": None,
                    "cancelled_request_interval": None,
                    "Начало обеда": format_time(lunch_interval[0]), 
                    "Конец обеда": format_time(lunch_interval[1])
                    # "lunch_interval": (format_time(lunch_interval[0]), format_time(lunch_interval[1]))
                })
                lunch_found = True
                break
        
        if not lunch_found:
            sorted_requests = sorted(time_intervals, key=lambda i: ((i[1] - i[0]).seconds, i[0]))
            for combo_length in range(1, len(sorted_requests) + 1):
                found_valid_combination = False
                for to_cancel in combinations(sorted_requests, combo_length):
                    remaining_intervals = [i for i in time_intervals if i not in to_cancel]
                    for lunch_interval in possible_lunch_intervals:
                        if all(not is_overlap(interval, lunch_interval, min_lunch_gap) for interval in remaining_intervals):
                            cancelled_ids = [requests["id"][time_intervals.index(i)] for i in to_cancel]
                            cancelled_intervals = [(format_time(i[0]), format_time(i[1])) for i in to_cancel]
                            results.append({
                                "Сотрудник ID": employee_id,
                                "cancelled_request_id": cancelled_ids,
                                "cancelled_request_interval": cancelled_intervals,
                                "Начало обеда": format_time(lunch_interval[0]), 
                                "Конец обеда": format_time(lunch_interval[1])
                                # "lunch_interval": (format_time(lunch_interval[0]), format_time(lunch_interval[1]))
                            })
                            lunch_found = True
                            found_valid_combination = True
                            break
                    if found_valid_combination:
                        break
                if lunch_found:
                    break
    
    return results

# загоняет df расписаний в массив для передачи в функцию определения обедов
def df_to_list_of_dicts(df):
    result = []
    
    # Группировка данных по сотруднику
    grouped = df.groupby('Сотрудник ID')
    
    for name, group in grouped:
        employee_data = {
            'Сотрудник ID': name,
            'work_start': group['Начало рабочего дня'].iloc[0],
            'work_end': group['Конец рабочего дня'].iloc[0],
            'requests': {
                'id': group['Задача ID'].tolist(),
                'time_intervals': list(zip(group['Начальное время выполнения'], group['Конечное время выполнения']))
            }
        }
        result.append(employee_data)
    
    return result

def add_lunch(df):
    """К итоговой таблице рассписания добавляет начало и конец обеда.
        Если у сотрудника плотный все занято и нет место для обеда, то освобождает место для обеды
    """
    df_dic = df_to_list_of_dicts(df)
    results = schedule_lunch(df_dic)

    canceled_task_id = sum([r['cancelled_request_id'] for r in results if r['cancelled_request_id']], [])
    df = df.loc[~df['Задача ID'].isin(canceled_task_id)].reset_index(drop=True)

    results = pd.DataFrame(results)

    df = df.merge(results[['Сотрудник ID', 'Начало обеда', 'Конец обеда']],
                   left_on='Сотрудник ID', 
                   right_on=['Сотрудник ID'],
                     how='left')#.to_excel('with_lunch.xlsx', index=False)
    return df

class TaskManager:
    def __init__(self, task_date) -> None:
        # self.task_zero_date = task_date - timedelta(hours=12)
        self.task_zero_date = datetime.strptime(task_date, "%Y-%m-%d") - timedelta(hours=12)
        # print('task_zero_date', self.task_zero_date)

    def to_minutes_since_noon_yesterday(self, dt):
        """Время в минутах начиная с task_zero_date"""

        return int((dt - self.task_zero_date).total_seconds() // 60)