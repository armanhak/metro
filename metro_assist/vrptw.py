import networkx as nx
from datetime import datetime, timedelta
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import json
import pandas as pd
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def convert_decimal_minutes_to_seconds(decimal_minutes):
    minutes = int(decimal_minutes)
    seconds = (decimal_minutes - minutes) * 100  # Преобразуем доли минут в секунды
    return minutes * 60 + int(seconds)

def convert_seconds_to_min(total_seconds):
    # hours, remainder = divmod(total_seconds, 60)
    minutes, seconds = divmod(total_seconds, 60)
    return minutes+ seconds/100
# @njit(parallel=True)
def fill_time_matrix(time_matrix, task_index_items, tasks, get_travel_time, num_tasks):
    task_cache = {task['id']: task for task in tasks}

    for i in range(num_tasks):
        task1_key, task1_value = task_index_items[i]
        task1_id = task1_key.split("_")[0]
        task1 = task_cache[task1_id]
        time_matrix[0, task1_value] = 0  # Время от депо до задачи
        time_matrix[task1_value, 0] = 0  # Время от задачи до депо
        for j in range(num_tasks):
            if i == j:
                continue
            task2_key, task2_value = task_index_items[j]
            task2_id = task2_key.split("_")[0]
            task2 = task_cache[task2_id]
            travel_time = get_travel_time(int(task1['id_st2']), int(task2['id_st1']))
            if task1['end'] + travel_time <= task2['start']-15:
                time_matrix[task1_value, task2_value] = travel_time + task1['duration']
            else:
                time_matrix[task1_value, task2_value] = 1000


class MetroVRPSolver:
    def __init__(self, workers, tasks, G):
        self.workers = workers
        self.tasks = tasks 
        self.G = G
        self.global_start_date = datetime.strptime('24.04.2024', "%d.%m.%Y") - timedelta(hours=12)
        self.load_data()

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

    def create_task_index(self):
        self.task_index = {}
        for task in self.tasks:
            for i in range(int(task['INSP_SEX_M'])):
                self.task_index[f"{task['id']}_M_{i+1}"] = len(self.task_index) + 1
            for i in range(int(task['INSP_SEX_F'])):
                self.task_index[f"{task['id']}_F_{i+1}"] = len(self.task_index) + 1

    def create_time_matrix(self):
        t = time.time()

        self.num_tasks = len(self.task_index)
        self.time_matrix = np.zeros((self.num_tasks + 1, self.num_tasks + 1), dtype=int)

        task_index_items = list(self.task_index.items())
        fill_time_matrix(self.time_matrix, 
                            task_index_items,
                                self.tasks,
                                self.get_travel_time, 
                                self.num_tasks)

        print('time_matr_time sec', time.time() - t)
    def create_data_model(self):
        self.data = {
            'time_matrix': self.time_matrix,
            'time_windows': [(0, 2880)] + [(task['start']-15, #инспектор должен быть на месте за 15 мин
                                             task['end']) for task in self.tasks for _ in range(int(task['INSP_SEX_M']) + int(task['INSP_SEX_F']))],
            'num_vehicles': len(self.workers),
            'depot': 0,
            'task_durations': [0] + [task['duration'] for task in self.tasks for _ in range(int(task['INSP_SEX_M']) + int(task['INSP_SEX_F']))]
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
        task_id = task_key.split("_")[0]
        task = next(task for task in self.tasks if task['id'] == task_id)
        worker_start, worker_end = worker['start'], worker['end']
        task_start, task_end = task['start'], task['end']
        # worker_sex = worker['SEX']
        # task_sex = task_key.split("_")[1]
        return worker_start <= task_start-15 and worker_end >= task_end

    def process_vehicle(self, vehicle_id):
        # t =  time.time()
        result = []
        index = self.routing.Start(vehicle_id)
        completed_tasks = 0
        while not self.routing.IsEnd(index):
            node_index = self.manager.IndexToNode(index)
            if node_index != self.data['depot']:
                taskid = list(self.task_index.keys())[list(self.task_index.values()).index(node_index)]
                task = next(task for task in self.tasks if task['id'] == taskid.split("_")[0])
                completed_tasks += 1

                # in_interval = self.workers[vehicle_id]["start"] <= task["start"] and self.workers[vehicle_id]["end"] >= task["end"]
                curr = (
                        self.workers[vehicle_id]["FIO"],
                        int(taskid.split('_')[0]),
                        int(self.workers[vehicle_id]["start"]),
                        int(self.workers[vehicle_id]["end"]),
                        int(task["start"]),
                        int(task["end"]),
                        int(task["end"])-int(task["start"]),
                        # in_interval,
                        int(task["id_st1"]),
                        int(task["id_st2"]),
                        task['status']
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

            r = pd.DataFrame(result, columns=['Сотрудник', 'Задача ID',
                                               'Начало рабочего дня',
                                               'Конец рабочего дня', 
                                               'Начальное время выполнения', 
                                               'Конечное время выполнения', 
                                               'Продолжительность', 
                                               'Начальная станция', 
                                                 'Конечная станция',
                                                 'status'
                                                 ])
            # stat = r[['Сотрудник ID', 'Продолжительность']].groupby(['Сотрудник ID']).agg(['count', 'mean', 'sum', 'min', 'max'])
            # stat.to_excel('stat.xlsx')
            # r.to_excel('Расписание.xlsx', index=False)
            
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
        futures = [executor.submit(solver.run) for solver in [solver_male, solver_female]]
        results = [f.result() for f in as_completed(futures)]

    results = pd.concat(results, axis=0, ignore_index=True)
    stat = results[['Сотрудник', 'Продолжительность']].groupby(['Сотрудник']).agg(['count', 'mean', 'sum', 'min', 'max'])
    
    stat.to_excel('stat.xlsx')
    results['Продолжительность']-=720 #12 часов, начало отсчета предыдущего дня
    for col in ['Начало рабочего дня', 
                'Конец рабочего дня', 
                'Начальное время выполнения',
                'Конечное время выполнения',
                'Продолжительность'
                ]:
        results[col] = results[col].map(convert_to_time)
    for col in ['Начальная станция', 'Конечная станция']:
        results[col] = results[col].replace(metro_id_name_dict)
    results.to_excel('Расписание.xlsx', index=False)

    print('Общее кол-во назанченных задач', len(results))
    print('overall_solve_time sec', (time.time()-st))
    print('all_poc_time', time.time()-allst)