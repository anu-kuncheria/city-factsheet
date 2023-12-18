import sys
sys.path.append("general_config")
import utility as util
from load_data import *


logger.info(f" Started script {os.path.basename(__file__)}")


def plot_marker(system_reclassify_four, boundary_path, markericon='circle'):
    """
    Create interactive web maps of locations via folium.
    """
    lat, lon = system_reclassify_four['ref_lat'].mean(
    ), system_reclassify_four['ref_long'].mean()
    map = folium.Map([lat, lon], width=750, height=700,
                     zoom_start=11, min_zoom=10)

    city_boundary = gpd.read_file(boundary_path)
    folium.GeoJson(data=city_boundary["geometry"]).add_to(map)
    locationarr = system_reclassify_four[[
        'nref_lat', 'nref_long']].values.tolist()

    for point in range(0, len(locationarr)):
        folium.Marker(locationarr[point],
                      popup=str(system_reclassify_four['ST_NAME'][point]) + ' ' +
                      str(system_reclassify_four['new_classi']
                          [point]) + ' ADT:'
                      + str(system_reclassify_four['adt'][point]),
                      icon=folium.Icon(color="red", icon=markericon, prefix='fa')).add_to(map)
    return map


def highestADT():
    system_metric = gpd.read_file(systemmetric_path)
    reclassifylinks = gpd.read_file(relinkspath)

    column = ['LINK_ID', 'new_classi', 'ST_NAME', 'FUNC_CLASS',
              'ref_lat', 'ref_long', 'nref_lat', 'nref_long', 'geometry']
    system_reclassify = system_metric[['LINK_ID', 'adt']].merge(
        reclassifylinks[column], left_on='LINK_ID', right_on='LINK_ID', how='left')
    system_reclassify_geom = gpd.GeoDataFrame(
        system_reclassify, geometry=system_reclassify['geometry'])
    system_reclassify_top = system_reclassify_geom.sort_values(
        'adt', ascending=False).groupby('new_classi').head(1)
    system_reclassify_top.reset_index(inplace=True)
    class_of_interest = ['Highway', 'Neighbourhood Residential street',
                         'Residential Throughway', 'Neighbourhood Commercial street']
    system_reclassify_four = system_reclassify_top[system_reclassify_top['new_classi'].isin(
        class_of_interest)]
    system_reclassify_four.reset_index(inplace=True)

    adt_table = system_reclassify_four[['ST_NAME', 'adt', 'new_classi']]
    adt_table.rename(columns={'ST_NAME': 'St Name',
                     'adt': 'ADT', 'new_classi': 'Class'}, inplace=True)
    adt_table.loc[:, "ADT"] = adt_table["ADT"].map('{:,d}'.format)
    print(adt_table)

    fig = plot_marker(system_reclassify_four, city_boundary_path)
    return fig, adt_table.style.hide_index()


if __name__ == "__main__":
    highestADT()
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
