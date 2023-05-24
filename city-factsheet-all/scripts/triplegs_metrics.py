import sys
sys.path.append("general_config")
from load_data import *
from utility import set_logger
from etl import taz_boundary_dissolve

logger.info(f" Started script {os.path.basename(__file__)}")
write_directory = os.path.join(processed_path,city_name, 'figures')

def total_trips():
    if city_name == 'scag':
        logger.info(f" Full simulation, loading the TAZ boundary")
        processed_legs_path = os.path.join(write_directory, 'b60legs.geojson')
    else:
        logger.info(f" Loading the city boundary")
        processed_legs_path = citylegs_path

    legs_city = gpd.read_file(processed_legs_path)
    total_trips = len(legs_city)
    return total_trips

def legs_purpose_bar():
    if city_name == 'scag':
        logger.info(f" Full simulation, loading the TAZ boundary")
        processed_legs_path = os.path.join(write_directory, 'b60legs.geojson')
    else:
        logger.info(f" Loading the city boundary")
        processed_legs_path = citylegs_path

    logger.info(f"Loading the city legs file")
    legs_city = gpd.read_file(processed_legs_path)
    
    if region_name == 'scag':
        logger.info(f"Using the trip purpose codes for legs file in {region_name}")
        purpose_code = {'home': [0], 'work':[1], 'university':[2], 'school':[3], 'shop':[5], 'eat out':[7,71,72,73], 'escort':[42, 411], 'maintenance':[6,61,62],'trucks':[90, 91, 92], 'others':[8,9,15]} # trip purpose specified in  demand model
    elif region_name == 'sacog':
        logger.info(f"Using the trip purpose codes for legs file in {region_name}")
        purpose_code = {'home': [0], 'work':[1],  'school':[2], 'escort':[3], 'pers.bus':[4], 'shop':[5], 'meal':[6],'social':[7], 'others':[10],'truck':[11]} 
   
    purpose_count = {i:0 for i in purpose_code.keys()}
    for k,v in purpose_code.items():
        purpose_count[k] = np.round(len(legs_city[legs_city['purpose'].isin(v)])/len(legs_city)*100)

    logger.info(f"Plotting the legs bar plot")
    width, height = 8,6
    fig1, (ax) = plt.subplots(1, 1, figsize=(width, height))
    t1 = plt.bar(*zip(*purpose_count.items()), width=0.7,align='center', figure = fig1)
    y = [v for v in purpose_count.values()]
    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in purpose_count.keys()]
    xlabs=[i for i in purpose_count.keys()]
    for i, v in enumerate(y):
        plt.text(i-.1, v + 0.02, str(int(v))+ '%')
    plt.xticks(xlocs, xlabs, rotation = 90)
    plt.xlabel("Trip purpose")
    plt.ylabel("Percentage of total")
    plt.title("Trips by Purpose")
    plt.tight_layout()
    logger.info(f"Writing the bar plot")
    fig1.savefig(os.path.join(write_directory, f"trippurpose_{city_name}.png"),bbox_inches='tight')

def worktrip_destination_heatmap():
    """
    Map showing work trip destinations.
    This may not be fully accurate work locations as we base the trip distribution based on population density.
    """
    if city_name == 'scag':
        logger.info(f" Full simulation, loading the TAZ boundary")
        processed_legs_path = os.path.join(write_directory, 'b60legs.geojson')
        city_boundry = taz_boundary_dissolve(taz_boundary_path)
    else:
        logger.info(f" Loading the city boundary")
        processed_legs_path = citylegs_path
        city_boundry = gpd.read_file(city_boundary_path)

    legs_city = gpd.read_file(processed_legs_path)
    workLegs = legs_city[legs_city['purpose']==1]
    lat = workLegs['end_lat'].mean()
    lon = workLegs['end_lon'].mean()
    m = folium.Map([lat,lon], width= 1300, height=700, zoom_start=11, min_zoom= 10)
    folium.GeoJson(data=city_boundry["geometry"]).add_to(m)
    locationarr = workLegs[['end_lat', 'end_lon']].values
    m.add_child(plugins.HeatMap(locationarr, radius=15))
    return m


if __name__ == '__main__':
    legs_purpose_bar()
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
    

