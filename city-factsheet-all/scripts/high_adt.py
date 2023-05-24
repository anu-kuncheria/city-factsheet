from utility import read_file, results_city_len
from load_data import *
import sys
sys.path.append("general_config")
pd.options.mode.chained_assignment = None


def plot_marker(system_reclassify_four, boundary_path, markericon='circle'):
    """
    Create interactive web maps of locations via folium.
    """
    lat, lon = system_reclassify_four['ref_lat'].mean(
    ), system_reclassify_four['ref_long'].mean()

    map = folium.Map([lat, lon], width=1300, height=700,
                     zoom_start=11, min_zoom=10)

    city_boundary = gpd.read_file(boundary_path)
    folium.GeoJson(data=city_boundary["geometry"]).add_to(map)
    locationarr = system_reclassify_four[[
        'nref_lat', 'nref_long']].values.tolist()
    for point in range(0, len(locationarr)):
        folium.Marker(locationarr[point],
                      popup=str(system_reclassify_four['ST_NAME'][point]) + ' ' + str(
                          system_reclassify_four['FUNC_CLASS'][point]) + ' ADT:' + str(system_reclassify_four['adt'][point]),
                      icon=folium.Icon(color="red", icon=markericon, prefix='fa')).add_to(map)
    return map


def highestADT():
    system_metric = gpd.read_file(systemmetric_path)
    system_metric_noramp = system_metric[system_metric['RAMP'] == 'N']
    system_reclassify_temp = system_metric_noramp.sort_values(
        'adt', ascending=False).groupby('FUNC_CLASS').head(2)
    # choosing only the links that has a street name , so the table has no null street name links
    system_reclassify_temp = system_reclassify_temp.dropna(how='any', axis=0)
    system_reclassify_top = system_reclassify_temp.drop_duplicates(
        subset='FUNC_CLASS', keep='first')
    print(system_reclassify_top['ST_NAME'])

    system_reclassify_top.reset_index(inplace=True)
    class_of_interest = [1, 2, 3, 4, 5]
    system_reclassify_four = system_reclassify_top[system_reclassify_top['FUNC_CLASS'].isin(
        class_of_interest)]
    system_reclassify_four.reset_index(inplace=True)

    adt_table = system_reclassify_four[['ST_NAME', 'adt', 'FUNC_CLASS']]
    adt_table.rename(columns={'ST_NAME': 'St Name', 'adt': 'ADT',
                     'FUNC_CLASS': 'Functional Class'}, inplace=True)
    adt_table.loc[:, "ADT"] = adt_table["ADT"].map('{:,d}'.format)

    # print(adt_table)
    print(system_reclassify_four.isnull().sum())

    fig = plot_marker(system_reclassify_four, city_boundary_path)
    return fig, adt_table.style.hide_index()


def truckHighestADT():
    city_links = gpd.read_file(citylinks_path)
    count = read_file(truckcount_path)
    countcity = count[count['link_id'].isin(city_links.LINK_ID)]
    countcity['adt'] = 0
    pd.options.mode.chained_assignment = None
    countcity.loc[:, 'adt'] = countcity.loc[:, "00:00":"23:45"].sum(axis=1)

    column = ['LINK_ID', 'ST_NAME', 'FUNC_CLASS', 'ref_lat',
              'ref_long', 'nref_lat', 'nref_long', 'geometry']
    truck_reclassify = countcity[['link_id', 'adt']].merge(
        city_links[column], left_on='link_id', right_on='LINK_ID', how='left')
    truck_reclassify_geom = gpd.GeoDataFrame(
        truck_reclassify, geometry=truck_reclassify['geometry'])
    truck_reclassify_geom_sort = truck_reclassify_geom.sort_values(
        'adt', ascending=False).groupby('FUNC_CLASS').head(1)
    truck_reclassify_geom_sort.reset_index(inplace=True)
    class_of_interest = [1, 2, 3, 4, 5]
    truck_reclassify_geom_four = truck_reclassify_geom_sort[truck_reclassify_geom_sort['FUNC_CLASS'].isin(
        class_of_interest)]
    truck_reclassify_geom_four.reset_index(inplace=True)

    truck_adt_table = truck_reclassify_geom_four[[
        'ST_NAME', 'adt', 'FUNC_CLASS']]
    truck_adt_table.rename(columns={
                           'ST_NAME': 'St Name', 'adt': 'ADT', 'FUNC_CLASS': 'Functional Class'}, inplace=True)
    truck_adt_table.loc[:, "ADT"] = truck_adt_table["ADT"].map('{:,d}'.format)

    fig = plot_marker(truck_reclassify_geom_four,
                      city_boundry, markericon='truck')
    return fig, truck_adt_table.style.hide_index()


if __name__ == "__main__":
    highestADT()
    if os.path.exists(truckcount_path):
        truckHighestADT()

    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
