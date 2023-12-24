# import csv
#
#
# def select_strong_signal_entries(csv_path, signal_threshold=-65):
#     selected_entries = []
#
#     with open(csv_path, mode='r', encoding='utf-8') as csv_file:
#         csv_reader = csv.DictReader(csv_file, delimiter=';')
#
#         for row in csv_reader:
#             signal_strength = float(row['signal'])
#
#             # Выбираем только записи с уровнем сигнала ниже порогового значения.
#             if signal_strength < signal_threshold:
#                 selected_entries.append(row)
#
#     return selected_entries
#
#
# ########
#
# selected_entries = select_strong_signal_entries("Data/wifi_logs_2022_12/wifi_logs_2022_12_01_202312081829.csv")
# field_names = ['guid', 'tm', 'router_mac', 'router_mac', 'user_mac', 'signal', 'router_id']
# with open('filtered_driving_users.csv', 'w', newline='') as csvfile:
#     writer = csv.DictWriter(csvfile, fieldnames=field_names, delimiter=';')
#     writer.writeheader()
#     writer.writerows(selected_entries)
# print(len(selected_entries))


import csv
from datetime import datetime, timedelta
from collections import defaultdict

def parse_time(time_str):
    return datetime.strptime(time_str.split(".")[0], "%Y-%m-%d %H:%M:%S")

# Обрабатываемые записи должны иметь сигнал существенно сильнее этого значения
SIGNAL_THRESHOLD = -70.0
# Максимальное время между записями для пользователя, чтобы считать, что он передвигается на автомобиле
MAX_TIME_DELTA = timedelta(seconds=150)

s = set()
def select_moving_cars(wifi_logs_csv):
    with open(wifi_logs_csv, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        car_candidates = defaultdict(list)
        for row in csv_reader:
            user_mac = row['user_mac'].strip('"')
            s.add(user_mac)
            signal_strength = float(row['signal'])
            if signal_strength > SIGNAL_THRESHOLD:
                tm = parse_time(row['tm'])
                # Если в списке уже есть запись для этого MAC-адреса
                if user_mac in car_candidates and car_candidates[user_mac]:
                    last_tm = car_candidates[user_mac][-1][1]
                    # Если предыдущая запись была слишком давно, начинаем накапливать новую серию фактов
                    if tm - last_tm > MAX_TIME_DELTA:
                        car_candidates[user_mac].clear()
                car_candidates[user_mac].append((row, tm))

        # Отбираем только те MAC-адреса, у которых есть две или более записей, удовлетворяющих критерию
        return {mac: entries for mac, entries in car_candidates.items() if len(entries) > 1}

# Пример использования функции:
cars_detected = select_moving_cars("Data/wifi_logs_2022_12/wifi_logs_2022_12_01_202312081829.csv")
print(len(s))
s2 = set()
for mac in cars_detected:
    s2.add(mac)
    print(mac, cars_detected[mac][0])
print(len(s))
print(len(s2))
