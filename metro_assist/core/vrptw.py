import networkx as nx
from datetime import datetime, timedelta
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import json
import pandas as pd
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import django
from .utils import make_aware_if_naive, time_to_seconds, time_to_min

# Установите переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metro_assist.settings')
# Настройка Django
# django.setup()
from core.utils import add_lunch

def convert_decimal_minutes_to_seconds(decimal_minutes):
    minutes = int(decimal_minutes)
    seconds = (decimal_minutes - minutes) * 100  # Преобразуем доли минут в секунды
    return minutes * 60 + int(seconds)

def convert_seconds_to_min(total_seconds):
    # hours, remainder = divmod(total_seconds, 60)
    minutes, seconds = divmod(total_seconds, 60)
    return minutes+ seconds/100
# @njit(parallel=True)



class MetroVRPSolver:
    def __init__(self, task_date, 
                 workers, 
                 tasks, 
                 task_time_matrix_dict,
                 G, 
                 task_sex = 'm', ):
        self.task_date = datetime.strptime(task_date, '%Y-%m-%d').date()
        self.task_zero_date = datetime.strptime(task_date, "%Y-%m-%d") - timedelta(hours=12)

        self.task_sex = task_sex
        self.workers = workers
        self.tasks = tasks 
        self.task_time_matrix_dict = task_time_matrix_dict
        self.G = G
        self.global_start_date = datetime.strptime('24.04.2024', "%d.%m.%Y") - timedelta(hours=12)
        self.load_data()


    def to_sec_since_noon_yesterday(self, dt):
        """Время в сеундах начиная с task_zero_date"""

        return int((make_aware_if_naive(dt)  - make_aware_if_naive(self.task_zero_date)).total_seconds() // 60)
        # return int((make_aware_if_naive(dt) - make_aware_if_naive(self.task_zero_date)).total_seconds())

    def combine_date_time_to_sec_since_noon_yesterday(self, d, t):
        combined_datetime = datetime.combine(d, t)
        return int(((make_aware_if_naive(combined_datetime) - make_aware_if_naive(self.task_zero_date)).total_seconds())//60)
    
    def load_data(self):
        self.create_task_index()
        self.create_time_matrix()
        self.create_data_model()

    def to_minutes_since_noon_yesterday(self, dt):
        return int((dt - self.global_start_date).total_seconds() // 60)

    def str_time_to_minutes(self, t):
        hours, minutes, seconds = map(int, t.split(':'))
        total_minutes = int(round(hours * 60 + minutes + seconds / 60))
        return total_minutes
    def str_time_to_sec(self, t):
        hours, minutes, seconds = map(int, t.split(':'))
        total_sec = hours * 60 + minutes + seconds
        return total_sec

    def create_task_index(self):
        self.task_index = {}
        for task in self.tasks:
            for i in range(int(task[f"insp_sex_{self.task_sex}"])):
                self.task_index[f"{task['id']}_{self.task_sex}_{i+1}"] = len(self.task_index) + 1

    def fill_time_matrix(self, task_index_items):
        task_cache = {task['id']: task for task in self.tasks}

        for i in range(self.num_tasks):
            task1_key, task1_value = task_index_items[i]
            task1_id = int(task1_key.split("_")[0])
            task1 = task_cache[task1_id]
            self.time_matrix[0, task1_value] = 0  # Время от депо до задачи
            self.time_matrix[task1_value, 0] = 0  # Время от задачи до депо
            for j in range(self.num_tasks):
                if i == j:
                    continue
                task2_key, task2_value = task_index_items[j]
                task2_id = int(task2_key.split("_")[0])
                task2 = task_cache[task2_id]

                time_from_task1_to_task2 = self.task_time_matrix_dict.get(f"{task1_id}-{task2_id}", 60000)
                
                self.time_matrix[task1_value, task2_value] = convert_seconds_to_min(time_from_task1_to_task2)


    def create_time_matrix(self):
        t = time.time()

        self.num_tasks = len(self.task_index)
        self.time_matrix = np.zeros((self.num_tasks + 1, self.num_tasks + 1), dtype=int)

        task_index_items = list(self.task_index.items())
        self.fill_time_matrix(task_index_items)

        print('time_matr_time sec', time.time() - t)
    def create_data_model(self):
        window_left = 15 #инспектор должен быть на месте за 15 мин
        depo_open = 2880
        self.data = {
            'time_matrix': self.time_matrix,
            'time_windows': [(0, depo_open)] + [(task['start'] - window_left, task['end']) for task in self.tasks
                                                for _ in range(int(task[f'insp_sex_{self.task_sex}']))],
            'num_vehicles': len(self.workers),
            'depot': 0,
            'task_durations': [0] + [task['end']-task['start'] for task in self.tasks for _ in range(int(task[f'insp_sex_{self.task_sex}']))]
        }

    def get_travel_time(self, from_station, to_station):

        travel_time =  int(nx.shortest_path_length(self.G,
                                               source=int(from_station), 
                                               target=int(to_station),
                                                 weight='weight'))
        travel_time = convert_seconds_to_min(travel_time)
        return travel_time
    def can_assign(self, worker_id, task_id):
        worker = self.workers[worker_id]
        task_key = list(self.task_index.keys())[list(self.task_index.values()).index(task_id)]
        task_id = int(task_key.split("_")[0])
        task = next(task for task in self.tasks if task['id'] == task_id)
        # worker_start, worker_end = worker['start'], worker['end']
        
        worker_start = worker['start']
        worker_end = worker['end']
                               
            # worker
        task_start = task['start']
        task_end = task['end']
        min_ = 15
        # print(worker_start,worker_end, task_start, task_end )
        return worker_start <= task_start - min_ and worker_end >= task_end

    def process_vehicle(self, vehicle_id):
        # t =  time.time()
        result = []
        index = self.routing.Start(vehicle_id)
        completed_tasks = 0
        while not self.routing.IsEnd(index):
            node_index = self.manager.IndexToNode(index)
            if node_index != self.data['depot']:
                taskid = list(self.task_index.keys())[list(self.task_index.values()).index(node_index)]
                task = next(task for task in self.tasks if task['id'] == int(taskid.split("_")[0]))
                completed_tasks += 1

                # in_interval = self.workers[vehicle_id]["start"] <= task["start"] and self.workers[vehicle_id]["end"] >= task["end"]
                curr = (
                        int(taskid.split('_')[0]),
                        self.workers[vehicle_id]["ID"],
                        self.workers[vehicle_id]["FIO"],
                        self.workers[vehicle_id]["SEX"],
                        

                        self.workers[vehicle_id]["start"],
                        self.workers[vehicle_id]['end'],
                        task["start"]-15,
                        # int(task["end"]),
                        task['end'],#int
                        task['end']-task['start'],
                        # in_interval,
                        int(task["id_st1_id"]),
                        int(task["id_st2_id"]),
                        # task['status']
                        )
                result.append(curr)
            index = self.solution.Value(self.routing.NextVar(index))
            time_ = self.solution.Value(self.time_dimension.CumulVar(index))
        # print('fetch_result_time sec', time.time()-t)
        return result, completed_tasks

    def solve(self):
        t = time.time()
        self.manager = pywrapcp.RoutingIndexManager(len(self.data['time_matrix']),
                                                    self.data['num_vehicles'], self.data['depot'])
        self.routing = pywrapcp.RoutingModel(self.manager)

        time_callback_index = self.routing.RegisterTransitCallback(self.time_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(time_callback_index)

        time_ = 'Time'
        self.routing.AddDimension(
            time_callback_index,
            120,
            2880,
            False,
            time_
        )

        self.time_dimension = self.routing.GetDimensionOrDie(time_)
        for location_idx, time_window in enumerate(self.data['time_windows']):
            if location_idx == 0:
                continue
            index = self.manager.NodeToIndex(location_idx)
            self.time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        for worker_id in range(self.data['num_vehicles']):
            for task_id in range(1, self.num_tasks + 1):
                if not self.can_assign(worker_id, task_id):
                    self.routing.VehicleVar(self.manager.NodeToIndex(task_id)).RemoveValue(worker_id)

        penalty = 10000000
        for task_id in range(1, self.num_tasks + 1):
            self.routing.AddDisjunction([self.manager.NodeToIndex(task_id)], penalty)

        demand_callback_index = self.routing.RegisterUnaryTransitCallback(self.demand_callback)
        self.routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            [sum(self.data['task_durations']) // self.data['num_vehicles']] * self.data['num_vehicles'],
            True,
            "Load"
        )

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.seconds = 60
        search_parameters.solution_limit = self.num_tasks
        search_parameters.lns_time_limit.seconds = 20
        self.solution = self.routing.SolveWithParameters(search_parameters)
        print('solve time sec', time.time()-t)
        return self.solution

    def run(self):
        if self.solve():
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.process_vehicle, vehicle_id) for vehicle_id in range(self.data['num_vehicles'])]
                results = [f.result() for f in as_completed(futures)]

            result = []
            completed_tasks_total = 0
            for vehicle_result, completed_tasks in results:
                result.extend(vehicle_result)
                completed_tasks_total += completed_tasks

            r = pd.DataFrame(result, columns=['Задача ID','Сотрудник ID','Сотрудник','Пол', 
                                               'Начало рабочего дня',
                                               'Конец рабочего дня', 
                                               'Начальное время выполнения', 
                                               'Конечное время выполнения', 
                                               'Продолжительность', 
                                               'Начальная станция', 
                                                 'Конечная станция',
                                                #  'status'
                                                 ])
            
            print(f'кол-во выполненных задач {completed_tasks_total}')
            return r
        else:
            print('Не удалось найти решение.')

    def time_callback(self, from_index, to_index):
        from_node = self.manager.IndexToNode(from_index)
        to_node = self.manager.IndexToNode(to_index)
        travel_time = self.data['time_matrix'][from_node][to_node]
        return travel_time

    def demand_callback(self, from_index):
        from_node = self.manager.IndexToNode(from_index)
        if from_node == self.data['depot']:
            return 0
        return self.data['task_durations'][from_node]



def load_workers_tasks(tasks_file, workers_file,
                       gender ='A',
                       wcount=None,
                       tcount=None
                       ):
    tdic = {"F":"Женский", "M":"Мужской"}
    global_start_date = datetime.strptime('24.04.2024', "%d.%m.%Y") - timedelta(hours=12)

    def str_time_to_minutes(t):
        hours, minutes, seconds = map(int, t.split(':'))
        total_minutes = int(round(hours * 60 + minutes + seconds / 60))
        return total_minutes
    def to_minutes_since_noon_yesterday(global_start_date, dt):
        return int((dt - global_start_date).total_seconds() // 60)

    with open(tasks_file, 'r', encoding="utf-8") as f:
        req = json.load(f)
        if tcount:
            req = req[:tcount]
    with open(workers_file, 'r', encoding="utf-8") as f:
        employers = json.load(f)
        if wcount:
            employers = employers[:wcount]

    req = pd.DataFrame(req)
    employers = pd.DataFrame(employers)
    req['datetime'] = pd.to_datetime(req['datetime'], dayfirst=True)

    employers[['start_work', 'end_work']] = employers['TIME_WORK'].str.split('-', expand=True)
    employers['start_work'] = employers["DATE"] + ' ' + employers['start_work']
    employers['end_work'] = '24.04.2024' + ' ' + employers['end_work']

    employers['start_work'] = pd.to_datetime(employers['start_work'], dayfirst=True)
    employers['end_work'] = pd.to_datetime(employers['end_work'], dayfirst=True)

    employers['start'] = employers['start_work'].map(lambda x: to_minutes_since_noon_yesterday(global_start_date, x))
    employers['end'] = employers['end_work'].map(lambda x: to_minutes_since_noon_yesterday(global_start_date, x))

    req['start'] = req['datetime'].map(lambda x: to_minutes_since_noon_yesterday(global_start_date, x))
    req['end'] = req['start'] + req['TIME_OVER'].map(str_time_to_minutes)
    req['duration'] = req['end'] - req['start']

    req['INSP_SEX_M'] = req['INSP_SEX_M'].astype(int)
    req['INSP_SEX_F'] = req['INSP_SEX_F'].astype(int)
    req = req.loc[~req['status'].isin([
                                       'Отмена', 
                                       'Отмена заявки по просьбе пассажира', 
                                       'Отмена заявки по неявке пассажира',
                                       'Отказ по регламенту',
                                       'Отказ',
                                       ])].reset_index(drop=True)
    if gender != 'A':
        employers = employers.loc[employers['SEX']==tdic[gender]].reset_index(drop=True)
        req = req.loc[req[f'INSP_SEX_{gender}']>0].reset_index(drop=True)
    if gender=="F":
        req[f'INSP_SEX_M'] = 0
    elif gender=="M":
        req[f'INSP_SEX_F'] = 0

    workers = employers[['ID', 'FIO', 'start', 'end', 'SEX']].to_dict(orient='records')
    tasks = req[['id', 'start', 'end', 'id_st1',
                  'id_st2', 'duration', 'status', 
                  'INSP_SEX_M', 'INSP_SEX_F']].to_dict(orient='records')

    return workers, tasks

def load_travel_transfer_data(travel_time_file, 
                              transfer_time_file
                              ):
    with open(travel_time_file, 'r') as f:
        travel_data = json.load(f)
    with open(transfer_time_file, 'r') as f:
        transfer_data = json.load(f)
    return travel_data, transfer_data

def create_graph(travel_data, transfer_data):
    G = nx.Graph()

    for entry in travel_data:
        st1 = int(entry['id_st1'])
        st2 = int(entry['id_st2'])
        time_ = float(entry['time'].replace(',', '.'))
        G.add_edge(st1, st2, weight=convert_decimal_minutes_to_seconds(time_), type='travel')

    for entry in transfer_data:
        st1 = int(entry['id1'])
        st2 = int(entry['id2'])
        time_ = float(entry['time'].replace(',', '.'))
        G.add_edge(st1, st2, weight=convert_decimal_minutes_to_seconds(time_), type='transfer')

    return G

def convert_to_time(minutes):
    base_time = pd.to_datetime("12:00", format="%H:%M")
    time = base_time + pd.to_timedelta(minutes, unit='m')
    return time.time()

def laod_metro_names(path):
    with open(path, 'r', encoding='utf-8') as f:
        metro = json.load(f)
    metro = {int(m['id']): m['name_station'] for m in metro}
    return metro

if __name__ == "__main__":
    allst = time.time()
    workers_file='./metro_assist/base_data/Сотрудники.json'
    tasks_file='./metro_assist/base_data/Заявки.json'
    travel_time_file='./metro_assist/base_data/Метро время между станциями.json'
    transfer_time_file='./metro_assist/base_data/Метро время пересадки между станциями.json'
    metro_name_file = './metro_assist/base_data/Наименование станций метро.json'
    
    prept = time.time()
    metro_id_name_dict = laod_metro_names(metro_name_file)

    travel_data, transfer_data = load_travel_transfer_data(travel_time_file, 
                                                           transfer_time_file)
    G = create_graph(travel_data=travel_data, 
                     transfer_data=transfer_data)

    workersm, tasksm = load_workers_tasks(tasks_file=tasks_file, 
                                        workers_file=workers_file, 
                                        gender='M',
                                        wcount=200, # all male employers
                                        tcount=600# all male requests
                                        )
    workersf, tasksf = load_workers_tasks(tasks_file=tasks_file, 
                                        workers_file=workers_file, 
                                        gender='F',
                                        wcount=200,#all female employers
                                        tcount=600, #all female requests
                                        )
    solver_female = MetroVRPSolver(
            workers=workersf,
            tasks=tasksf,
            G = G
        )
    solver_male = MetroVRPSolver(
            workers=workersm,
            tasks=tasksm,
            G=G
        )
     
    print('end_prep time sec', (time.time()-prept))
    print('Начало распределения задач')
    st = time.time()

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(solver.run) for solver in [solver_male, 
                                                              solver_female]]
        results = [f.result() for f in as_completed(futures)]

    results = pd.concat(results, axis=0, ignore_index=True)

    for col in [
                'Начало рабочего дня', 
                'Конец рабочего дня', 
                # 'Начальное время выполнения',
                'Конечное время выполнения',
                # 'Продолжительность'
                ]:
        results[col] = results[col].map(convert_to_time)

    results = add_lunch(results)# добавим время обеда

    stat = results[['Сотрудник', 'Продолжительность']].groupby(['Сотрудник']).agg(['count', 'mean', 'sum', 'min', 'max'])    
    stat.to_excel('stat.xlsx')# Сохраним статистику по времени выполнению задач

    results['Продолжительность']-=720 #12 часов, начало отсчета предыдущего дня
    results['Продолжительность'] = results['Продолжительность'].map(convert_to_time)


    for col in ['Начальная станция', 'Конечная станция']:
        results[col] = results[col].replace(metro_id_name_dict)
    results.to_excel('Расписание.xlsx', index=False)

    print('Общее кол-во назанченных задач', len(results))
    print('overall_solve_time sec', (time.time()-st))
    print('all_poc_time', time.time()-allst)