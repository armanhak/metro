import networkx as nx
from .models import MetroTravelTime, MetroTransferTime

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