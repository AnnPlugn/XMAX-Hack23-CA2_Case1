import folium
import csv
import geopandas as gpd

def main():
    create_a_router_map()
    trafic()
    # Сохранение карты в HTML
    my_map.save('my_interactive_map.html')




map_center = (54.193122, 37.617348)
my_map = folium.Map(location=map_center, zoom_start=10)

# Переводим координаты из таблицы в формат кортажа
def convert_point_format(point_str):
    # Удаляем 'POINT (' и ')' из строки и разделяем оставшуюся часть по пробелу
    lon, lat = point_str.replace('POINT (', '').replace(')', '').split()
    # Конвертируем значения в float и возвращаем в правильном порядке
    return float(lat), float(lon)

def create_a_router_map():
    # Создаем карту с центром в определенной точке
    # Центр карты - город Тула


    # Список координат, которые мы хотим отметить на карте
    # coordinates = [
    #     (54.204617, 37.618886),  # 1 роутер (0648078a-9d45-4577-af14-12b49e8f017b)
    #     (54.1688958982062, 37.5826629190378),  # 2 роутер (6422a0a5-2c2d-4610-bebc-91722ea37827)
    #     # Другие координаты
    # ]

    coordinates = {

    }


    with open('wifi_routers.csv') as file_obj:
        header = next(file_obj)
        reader_obj = csv.reader(file_obj, delimiter=';')
        for row in reader_obj:
            point_guid = row[0]
            point_cor = row[1]
            print(row[1])
            point_tuple = convert_point_format(point_cor)
            coordinates[point_guid] = point_tuple

    print(coordinates)





    # Добавляем маркеры на карту
    for point_guid in coordinates:
        folium.Marker(
            location=coordinates[point_guid],
            popup=f'<b>{point_guid}</b>',  # HTML с описанием места
        ).add_to(my_map)



def trafic():

    # Загрузка геоданных
    data_path = 'road_network.csv'
    gdf = gpd.read_file(data_path, delimiter=';')

    # Преобразование строки LINESTRING в объект LineString с настройкой SRID (координатной системы проекции)
    gdf['geometry'] = gpd.GeoSeries.from_wkt(gdf['geom'])
    gdf.crs = "EPSG:4326"  # WGS 84

    # Определяем границы города Тула (здесь используем примерный прямоугольник, вам нужно задать точные границы)
    tula_bounds = ('POLYGON ((37.617346 54.193124,37.543865 54.109067,37.536175 54.091236,37.616406 54.089069,37.616406 54.089069,37.616406 54.089069,37.735046 54.209524,37.621587 54.300247,37.505231 54.204646,37.617346 54.193124))')
    tula_polygon = gpd.GeoSeries.from_wkt([tula_bounds], crs="EPSG:4326")

    # Отфильтровываем только те записи, которые находятся внутри границ города Тула
    gdf = gdf[gdf.intersects(tula_polygon.geometry[0])]

    # Если датафрейм всё ещё слишком велик, можно упростить геометрию
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.0001)


    # Отображение на карте дорог с учетом веса трафиκа
    for index, row in gdf.iterrows():
        weight = row['weight']
        color = 'green' if float(weight) < 100 else 'orange' if float(weight) < 300 else 'red'
        folium.PolyLine(
            locations=[(pt[1], pt[0]) for pt in row['geometry'].coords],
            color=color,
            weight=2,
            opacity=0.7
        ).add_to(my_map)




main()