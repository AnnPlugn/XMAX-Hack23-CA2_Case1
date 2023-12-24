import os
import folium
import warnings
import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point

warnings.filterwarnings('ignore')
pd.options.display.max_colwidth = 10000000000

#Карта с центром в городе Тула
map_center = (54.193122, 37.617348)
my_map = folium.Map(location=map_center, zoom_start=12)

# Функция для удаления 'POINT (' и ')' из строки и получения коопдинат в нужном формате
def convert_ruter_point_format(point_str):
    lon, lat = point_str.replace('POINT (', '').replace(')', '').split()
    return float(lat), float(lon)


coordinates = {
        # "id точки" : (x, y)
}

folder_path = 'C:/Users/elnur/PycharmProjects/Хакатон'
file_names = os.listdir(folder_path)
print(file_names)
# Загрузка данных о роутерах
routers_df = pd.read_csv('Data/wifi_routers.csv', sep=';')
routers_df.drop('address_json', axis=1, inplace=True)
routers_df.rename(columns={"guid": "router_id", "geom": "cords"}, inplace=True)

# Преобразование координат роутеров в числовые значения
routers_df[['lon', 'lat']] = routers_df['cords'].str.extract(r'POINT \(([^ ]+) ([^ ]+)\)')
routers_df['lon'] = routers_df['lon'].astype(float)
routers_df['lat'] = routers_df['lat'].astype(float)
routers_df.drop('cords', axis=1, inplace=True)

# Меняем местами 'lat' и 'lon' для удобства
cols = list(routers_df.columns)
a, b = cols.index('lat'), cols.index('lon')
cols[b], cols[a] = cols[a], cols[b]
routers_df = routers_df[cols]

print(routers_df.to_string(index=False))

lst_router_ids = routers_df['router_id'].tolist()
lst_cords_lat = routers_df['lat'].tolist()
lst_cords_lon = routers_df['lon'].tolist()

dct_router_ids = {

}

for id in range(len(lst_router_ids)):
    dct_router_ids[lst_router_ids[id]] = (lst_cords_lat[id], lst_cords_lon[id])
    folium.Marker(
        location=dct_router_ids[lst_router_ids[id]],
        popup=f'<b>{lst_router_ids[id]}</b>',  # HTML с описанием места
    ).add_to(my_map)

my_map.save('Results/routers_map.html')
print('Интерактивная карта c маркерами роутеров создана под названием "routers_map.html"!')
print('\n')


        ###Обозначение дорог входящих в Тулу###

road_network_df = gpd.read_file('Data/road_network.csv', delimiter=';')
# Преобразование строки LINESTRING в объект SRID (координатной системы проекции)
road_network_df['geometry'] = gpd.GeoSeries.from_wkt(road_network_df['geom'])
road_network_df.crs = "EPSG:4326"  # WGS 84
print('\n')

print('Количество дорог в файле:', len(road_network_df))
# Определяем границы города Тула
tula_bounds = ('POLYGON ((37.615391 54.299588, 37.599529 54.294949, 37.578134 54.260350, 37.577556  54.242430, 37.559656 54.228246, 37.540086 54.219707, 37.506359 54.204942, 37.503236 54.148150, 37.553202 54.150839, 37.520308 54.136293, 37.511555 54.124678, 37.549862 54.097276, 37.595247 54.091035, 37.635428 54.094951, 37.639383 54.115627, 37.596759 54.129127, 37.652934 54.144292, 37.658479 54.192012, 37.695077 54.150803, 37.736110 54.133873, 37.737588 54.152756, 37.733522 54.186592, 37.730934 54.201116, 37.718596 54.223076, 37.615391 54.299588))')
tula_polygon = gpd.GeoSeries.from_wkt([tula_bounds], crs="EPSG:4326")

# Отфильтровываем только те записи, которые находятся внутри границ города Тула
road_network_df = road_network_df[road_network_df.intersects(tula_polygon.geometry[0])]


print('Количество дорог в Туле:', len(road_network_df))
print('\n')

# Упрощение геометрии
road_network_df['geometry'] = road_network_df['geometry'].simplify(tolerance=0.0001)


# Отображение дорог на карте
for index, row in road_network_df.iterrows():
    # weight = row['weight']
    folium.PolyLine(
        locations=[(pt[1], pt[0]) for pt in row['geometry'].coords],
        color='green',
        weight=2,
        opacity=0.7,
        icon=folium.Icon(color='blue')
    ).add_to(my_map)
my_map.save('Results/roads_and_routers_map.html')
print('Интерактивная карта c дорогами и роутерами внутри Тулы создана под названием "roads_and_routers_map.html"!')
print('\n')


        ###Поиск ближайшего роутера для каждой дороги###

# Загрузка данных о логах Wi-Fi с датами
wifi_logs_df = pd.read_csv('Data/wifi_logs_2022_12_01_202312081829.csv', sep=';', parse_dates=['tm'])



print(road_network_df)
print('\n')
print(wifi_logs_df)
print('\n')







# Конвертируем датафреймы pandas в геодатафреймы geopandas
gdf_road_network = gpd.GeoDataFrame(
    road_network_df,
    geometry=road_network_df['geom'].apply(wkt.loads),
    crs={'init': 'epsg:4326'}
)
gdf_routers = gpd.GeoDataFrame(
    routers_df,
    geometry=gpd.points_from_xy(routers_df['lon'], routers_df['lat']),
    crs={'init': 'epsg:4326'}
)

# Сопоставим каждого роутера с ближайшей дорогой
def assign_nearest_road(point, roads_gdf):
    nearest_router = roads_gdf.geometry.distance(point).idxmin()
    print(roads_gdf.loc[nearest_router]['router_id'])
    return roads_gdf.loc[nearest_router]

# Создаем пустой столбец в датафрейме с дорожной сетью для хранения ID ближайшего роутера
gdf_road_network['nearest_router_id'] = None

# Сопоставляем каждую дорогу с ближайшим роутером
for _, road_row in gdf_road_network.iterrows():
    nearest_router = assign_nearest_road(road_row.geometry, gdf_routers)
    gdf_road_network.at[road_row.name, 'nearest_router_id'] = nearest_router['router_id']

print(gdf_road_network)



print('\n')
excel = 'Results/gdf_road_network.xlsx'
gdf_road_network.to_excel(excel, index=False)
print(f'Таблица {excel} успешло создана!')


