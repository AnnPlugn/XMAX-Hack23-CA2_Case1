import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

folder_path = 'C:/Users/aplyg/PycharmProjects/X-max_CA_2/Week'
file_names = os.listdir(folder_path)
morning_range = ('06:00:00', '09:59:59')
day_range = ('10:00:00', '17:59:59')
evening_range = ('18:00:00', '23:59:59')
night_range = ('00:00:00', '05:59:59')
wifi_routers_df = pd.read_csv('wifi_routers.csv', sep=';')
road_network_df = pd.read_csv('road_networkx.csv', delimiter=';')

def plot_average_trip_times(average_trip_times):
    plt.figure(figsize=(10, 6))
    plt.bar(average_trip_times['Time Range'], average_trip_times['Average Trip Time'], color='skyblue')
    plt.title('Среднее время для каждого промежутка времени')
    plt.xlabel('Промежуток времени')
    plt.ylabel('Среднее время поездки в секундах')
    plt.show()
def get_time_range(time):
    time = datetime.strptime(str(time), "%Y-%m-%d %H:%M:%S%z").time()
    if datetime.strptime(morning_range[0], "%H:%M:%S").time() <= time <= datetime.strptime(morning_range[1], "%H:%M:%S").time():
        return 'Morning'
    elif datetime.strptime(day_range[0], "%H:%M:%S").time() <= time <= datetime.strptime(day_range[1], "%H:%M:%S").time():
        return 'Day'
    elif datetime.strptime(evening_range[0], "%H:%M:%S").time() <= time <= datetime.strptime(evening_range[1], "%H:%M:%S").time():
        return 'Evening'
    else:
        return 'Night'
def calculate_average_trip_time(wifi_logs_df):
    wifi_logs_df['tm'] = pd.to_datetime(wifi_logs_df['tm'])
    wifi_logs_df['time_range'] = wifi_logs_df['tm'].apply(lambda x: get_time_range(x))
    wifi_logs_df['user_mac'] = wifi_logs_df['user_mac'].astype(str)
    wifi_logs_df['tm'] = pd.to_datetime(wifi_logs_df['tm'])
    user_trip_times = []
    for time_range in ['Morning', 'Day', 'Evening']:
        time_filtered_df = wifi_logs_df[wifi_logs_df['time_range'] == time_range]
        user_trips = time_filtered_df.groupby('user_mac').agg({'tm': ['min', 'max']})
        user_trips.columns = ['min_tm', 'max_tm']
        user_trips['trip_time'] = (user_trips['max_tm'] - user_trips['min_tm']).dt.total_seconds()
        average_trip_time = user_trips['trip_time'].mean()
        user_trip_times.append((time_range, average_trip_time))
    return pd.DataFrame(user_trip_times, columns=['Time Range', 'Average Trip Time'])

all_results = []
for file_name in file_names:
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path, delimiter=';')
    average_trip_times = calculate_average_trip_time(df)
    all_results.append(average_trip_times)
    plot_average_trip_times(average_trip_times)
all_results_df = pd.concat(all_results, axis=0)
print(all_results_df)




