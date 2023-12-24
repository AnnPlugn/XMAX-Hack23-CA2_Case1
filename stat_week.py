import pandas as pd
from datetime import datetime
import os
import seaborn as sns
import matplotlib.pyplot as plt


folder_path = 'C:/Users/aplyg/PycharmProjects/X-max_CA_2/Analyse/Week'
file_names = os.listdir(folder_path)
morning_range = ('06:00:00', '09:59:59')
day_range = ('10:00:00', '17:59:59')
evening_range = ('18:00:00', '23:59:59')
night_range = ('00:00:00', '05:59:59')
wifi_routers_df = pd.read_csv('wifi_routers.csv', sep=';')
road_network_df = pd.read_csv('road_networkx.csv', delimiter=';')

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

def count_trans(wifi_logs_df):
    wifi_logs_df['tm'] = pd.to_datetime(wifi_logs_df['tm'])
    wifi_logs_df['time_range'] = wifi_logs_df['tm'].apply(lambda x: get_time_range(x))
    aggregated_df = wifi_logs_df.groupby(['router_id', 'time_range', 'tm', 'signal', 'user_mac']).size().reset_index(name='count')
    total_traffic = aggregated_df['count'].sum()
    print('Общее количество перемещений: {}'.format(total_traffic))
    merged_df = wifi_logs_df.merge(wifi_routers_df, left_on='router_id', right_on='guid', how='inner')
    day_traffic = merged_df.groupby('time_range').agg({
        'signal': 'mean',
        'router_mac': 'count'
    }).reset_index()
    return day_traffic

all_results = []
for file_name in file_names:
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path, delimiter=';')
    result = count_trans(df)
    all_results.append(result)
all_results_df = pd.concat(all_results, axis=0)
all_results_df.to_excel('av_time_week.xlsx', index=False)
def df_get():
    return all_results_df
# Визуализация интенсивности дорожного трафика
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
all_results_df.plot(x='time_range', y='signal', kind='bar', ax=axes[0])
axes[0].set_title('Week Traffic Intensity')
axes[0].set_ylabel('Signal Strength')

# Визуализация количества подключений к роутерам
all_results_df.plot(x='time_range', y='router_mac', kind='bar', ax=axes[1])
axes[1].set_title('Weekday Connections')
axes[1].set_ylabel('Number of Connections')

plt.tight_layout()
plt.show()