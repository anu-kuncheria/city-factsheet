import sys
sys.path.append("general_config")
from load_data import *
import utility as util

logger.info(f" Started script {os.path.basename(__file__)}")
write_directory = os.path.join(processed_path, city_name, 'figures')


def total_trips():
    legs_city = gpd.read_file(citylegs_path)
    total_trips = len(legs_city)
    return total_trips


def legs_purpose_bar():
    legs_city = gpd.read_file(citylegs_path)
    if region_name == "sanfrancisco_bay_area":
        purpose_code = {'home': [0], 'work': [1], 'school': [2], 'escort': [3], 'pers.bus': [
            4], 'shop': [5], 'meal': [6], 'social': [7], 'others': [10], 'truck': [11]}

    purpose_count = {i: 0 for i in purpose_code.keys()}
    for k, v in purpose_code.items():
        purpose_count[k] = np.round(
            len(legs_city[legs_city['purpose'].isin(v)]) / len(legs_city) * 100)

    width, height = 8, 6
    fig1, (ax) = plt.subplots(1, 1, figsize=(width, height))
    t1 = plt.bar(*zip(*purpose_count.items()),
                 width=0.7, align='center', figure=fig1)
    y = [v for v in purpose_count.values()]
    xlocs, xlabs = plt.xticks()
    xlocs = [i for i in purpose_count.keys()]
    xlabs = [i for i in purpose_count.keys()]
    for i, v in enumerate(y):
        plt.text(i - .1, v + 0.02, str(int(v)) + '%')
    plt.xticks(xlocs, xlabs, rotation=90)
    plt.xlabel("Trip purpose")
    plt.ylabel("Percentage of total")
    plt.title("Trips by Purpose")
    plt.tight_layout()
    fig1.savefig(os.path.join(write_directory,
                 f"trippurpose_{city_name}.png"), bbox_inches='tight')


def origin_vmt_residential():
    legs_vmt = gpd.read_file(os.path.join(
        legspath, city_name, f"legs_startvmt_{city_name}.geojson"))
    lat = legs_vmt['start_lat'].mean()
    lon = legs_vmt['start_lon'].mean()
    m = folium.Map([lat, lon], width=750, height=700,
                   zoom_start=11, min_zoom=10)
    city_boundry = gpd.read_file(boundry_file)
    folium.GeoJson(data=city_boundry["geometry"]).add_to(m)

    locationarr = legs_vmt[['start_lat', 'start_lon', 'total dist']].values
    m.add_child(plugins.HeatMap(locationarr, radius=15))
    return m


def worktrip_destination_heatmap():
    """
    Map showing work trip destinations.
    This may not be fully accurate work locations as we base the trip distribution based on population density.
    """
    city_boundry = gpd.read_file(city_boundary_path)
    legs_city = gpd.read_file(citylegs_path)
    workLegs = legs_city[legs_city['purpose'] == 1]
    lat = workLegs['end_lat'].mean()
    lon = workLegs['end_lon'].mean()
    m = folium.Map([lat, lon], width=1300, height=700,
                   zoom_start=11, min_zoom=10)
    folium.GeoJson(data=city_boundry["geometry"]).add_to(m)
    locationarr = workLegs[['end_lat', 'end_lon']].values
    m.add_child(plugins.HeatMap(locationarr, radius=15))
    return m


if __name__ == '__main__':
    legs_purpose_bar()
    worktrip_destination_heatmap()
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
