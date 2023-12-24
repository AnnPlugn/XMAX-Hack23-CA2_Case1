import pandas as pd
from datetime import datetime
import os
import seaborn as sns
import matplotlib.pyplot as plt

folder_path = 'C:/Users/aplyg/PycharmProjects/X-max_CA_2/Новая папка'
file_names = os.listdir(folder_path)
morning_range = ('06:00:00', '09:59:59')
day_range = ('10:00:00', '17:59:59')
evening_range = ('18:00:00', '23:59:59')
night_range = ('00:00:00', '05:59:59')
df = pd.read_csv('wifi_routers.csv', sep=';')
road_network_df = pd.read_csv('road_networkx.csv', delimiter=';')

def get_time_range(time):
    time = datetime.strptime(str(time), "%Y-%m-%d %H:%M:%S%z").time()
    if datetime.strptime(morning_range[0], "%H:%M:%S").time() <= time <= datetime.strptime(morning_range[1],
                                                                                           "%H:%M:%S").time():
        return 'Morning'
    elif datetime.strptime(day_range[0], "%H:%M:%S").time() <= time <= datetime.strptime(day_range[1],
                                                                                         "%H:%M:%S").time():
        return 'Day'
    elif datetime.strptime(evening_range[0], "%H:%M:%S").time() <= time <= datetime.strptime(evening_range[1],
                                                                                             "%H:%M:%S").time():
        return 'Evening'
    else:
        return 'Night'


def count_trans(wifi_logs_df, date):
    wifi_logs_df['tm'] = pd.to_datetime(wifi_logs_df['tm'])
    wifi_logs_df['time_range'] = wifi_logs_df['tm'].apply(get_time_range)
    aggregated_df = wifi_logs_df.groupby(['router_id', 'time_range']).size().reset_index(name='count')

    router_traffic = aggregated_df.groupby('router_id')['count'].sum().reset_index()
    counts = router_traffic['count'].tolist()

    results_df = pd.DataFrame({'Day': [date] * len(router_traffic), 'Router Number': router_traffic['router_id'], 'Connections': counts})
    return results_df

all_results = []
for file_name in file_names:
    file_path = os.path.join(folder_path, file_name)
    date = file_name[10:20]
    df = pd.read_csv(file_path, delimiter=';')
    result = count_trans(df, date)
    all_results.append(result)

all_results_df = pd.concat(all_results)
all_results_df.to_excel('all_res.xlsx', index=False)


# Предположим, что у вас уже есть DataFrame all_results_df с данными о подключениях к роутерам

# Создаем столбчатую диаграмму с помощью библиотеки seaborn
plt.figure(figsize=(12, 8))
bar_plot = sns.barplot(x='Router Number', y='Connections', hue='Day', data=all_results_df)
bar_plot.set_title('Изменения подключений к роутерам')
bar_plot.set_xlabel('Номер роутера')
bar_plot.set_ylabel('Количество подключений')

# Поворачиваем подписи оси x для лучшей читаемости
plt.xticks(rotation=45)

# Отображаем график
plt.show()