"""
Generates:
1. Clipped city links geojson file
2. Clipped city legs geojson file
3. Clipped city reclassified links geojson file
4. Clipped city regulator geojson file
"""
import sys
sys.path.append("general_config")
from load_data import *
import utility as util



logger.info(f"Load config from {config_file}")
logger.info(f" city_name specified in config is {city_name}")
logger.info(f" Started script {os.path.basename(__file__)}")

write_directory = os.path.join(processed_path, city_name)


def gdf_wholenetwork():
    logger.info(
        "-------------------Start Whole network GDF transformation-------------------")
    links = pd.read_csv(links_path)
    nodes = pd.read_csv(nodes_path)
    gdf_links, gdf_nodes = util.networkGeom(links, nodes, crs="epsg:4326")
    gdf_links.to_file(gdflinks_path, driver="GeoJSON")
    logger.info(
        "-------------------Finished Whole network GDF transformation-------------------")


def whole_legs_to_geojson():
    logger.info("-----------------Started converting the whole legs file to geojson. The geometry is based on trip end node.--------------")
    cols = ['leg id', 'mode', 'purpose', 'energy cat.', 'start node', 'end node',
            'duration (congested)', 'total distance (m)', 'total fuel consumed']
    legs = pd.read_csv(raw_legs_path, sep='\t', usecols=cols)
    nodes = pd.read_csv(nodes_path, usecols=['NODE_ID', 'LAT', 'LON'])
    legs = legs.merge(nodes[['NODE_ID', 'LAT', 'LON']],
                      left_on='end node', right_on='NODE_ID')
    legs = legs.rename(columns={'LAT': 'end_lat', 'LON': 'end_lon'})
    logger.info("legs loaded in", len(legs))

    print(" Creating the geometry series")
    s = gpd.GeoSeries([Point(x, y)
                      for x, y in zip(legs['end_lon'], legs['end_lat'])])
    print(" Creating geodataframe using the geoseries")
    gdf_legs = gpd.GeoDataFrame(legs, geometry=s)
    print("Geodataframe created", len(gdf_legs))

    print("Started writing the file to geojson in chunks")
    outputpath = os.path.join(processed_path, city_name, 'b60legs.geojson')
    chunksize = 1000000
    total_chunks = (len(gdf_legs) // chunksize) + 1
    with open(outputpath, "w") as f:
        counter = 0
        for chunk in gdf_legs.groupby(gdf_legs.index // chunksize):
            counter += 1
            print(f"Writing chunk {counter} of total {total_chunks} chunks")
            chunk[1].to_file(outputpath, driver="GeoJSON",
                             mode='a' if counter > 1 else 'w')
    print("---------------- Completed writing whole legs geojson ----------------------s")


# region boundary obtained from web. It has all city boundary in the region
def filter_cityboundary_from_regionboundary(regioncities_boundary_path, cityname_in_boundaryfile):
    region = gpd.read_file(regioncities_boundary_path)
    city_boundary = region[region['city'] == cityname_in_boundaryfile]
    if not city_boundary.crs == 'EPSG:4326':
        city_boundary = city_boundary.to_crs(4326)
    city_boundary.to_file(os.path.join(
        write_directory, f"boundary_{city_name}.geojson"), driver="GeoJSON")


def network_clipping(boundary_path):
    """
    Loads whole GDF network and filters the respective city links based on city boundry
    """
    logger.info(
        "-------------------Start data transformation-------------------")
    logger.info(f"==== Loading the city boundry and GDF links file ====")
    city_boundary = gpd.read_file(boundary_path)
    assert city_boundary.crs == 'EPSG:4326', "CRS not epsg 4326. Check the CRS of the boundry shapefile"
    gdf_links = gpd.read_file(gdflinks_path)
    logger.info("Clipping the network to city boundry.")
    city_links = gpd.clip(gdf_links, city_boundary)
    city_links = city_links[city_links['geometry'].apply(
        lambda x: x.type == 'LineString')]
    print(len(city_links))
    print(city_links.crs)
    logger.info(f"Number of links in the city: {len(city_links)}")
    logger.info("End data transformation")
    # export data
    logger.info(f"write data to {processed_path}")
    city_links.to_file(os.path.join(
        write_directory, f"citylinks_{city_name}.geojson"), driver="GeoJSON")
    logger.info(f" # links: {len(city_links)}")
    logger.info(
        "---------------- Completed links processing -------------------")


def legs_city_based_clippedlinks():
    """
    This is faster than loading the whole legs geojson
    """
    logger.info("------------- Loading the raw legs csv ---------------s")
    cols = ['leg id', 'mode', 'purpose', 'energy cat.', 'start node', 'end node',
            'duration (congested)', 'total distance (m)', 'total fuel consumed']
    legs = pd.read_csv(raw_legs_path, sep='\t', usecols=cols)

    logger.info("==== Loading the clipped city links ===")
    city_links = gpd.read_file(citylinks_path)
    citynodeslist = set(
        list(city_links['REF_IN_ID'].values) + list(city_links['NREF_IN_ID'].values))
    logger.info("==== Filtering legs based on city nodes ===")
    legs_end = legs[(legs['end node'].isin(citynodeslist))]

    logger.info(
        "==== Transforming the  filtered legs that end in the city to geodata ===")
    nodes = pd.read_csv(nodes_path, usecols=['NODE_ID', 'LAT', 'LON'])
    legs_end = legs_end.merge(
        nodes[['NODE_ID', 'LAT', 'LON']], left_on='end node', right_on='NODE_ID')
    legs_end = legs_end.rename(columns={'LAT': 'end_lat', 'LON': 'end_lon'})
    print(" Creating the geometry series")
    s = gpd.GeoSeries([Point(x, y) for x, y in zip(
        legs_end['end_lon'], legs_end['end_lat'])])
    print(" Creating geodataframe using the geoseries")
    gdf_legs_end = gpd.GeoDataFrame(legs_end, geometry=s)
    print("Geodataframe created", len(gdf_legs_end))

    logger.info(f"Writing data to {processed_path}")
    gdf_legs_end.to_file(os.path.join(
        write_directory, f"citylegs_{city_name}.geojson"), driver="GeoJSON")
    logger.info(f" # legs: {len(gdf_legs_end)}")
    logger.info(
        " -------------- Completed city legs processing ---------------------")


def reclassify_network_clipping(boundary_path):
    if relinkspath != '':
        logger.info("==== Loading the reclassified links shapefile  ===")
        relinks = gpd.read_file(relinkspath)
        city_boundry = gpd.read_file(boundary_path)
        recity_links = gpd.clip(relinks, city_boundry)
        recity_links = recity_links[recity_links['geometry'].apply(
            lambda x: x.type == 'LineString')]
        # export data
        logger.info(f" Writing data to {processed_path}")
        recity_links.to_file(os.path.join(
            write_directory, f"reclassifylinks_{city_name}.geojson"), driver="GeoJSON")
        logger.info(f" # reclassify links: {len(recity_links)}")
        logger.info(f" # reclassify links columns: {recity_links.columns}")
        logger.info(" ==== Completed reclassiffied links processing ====")
    else:
        logger.info("==== No reclassified links path  ===")


def regulator_preprocessing():
    """
    The regular file is from Dimitris. The file has a column 'y_pred_rf_final'. It denotes 0 is uncontrolled, 1 stop signs and 2 traffic signals.
    """
    traffic_regulator = pd.read_csv(rawregulatorpath)
    traffic_regulator['signal_id'] = np.where(
        traffic_regulator['supernode_id'] == 999999999999999999, traffic_regulator['node_id'], traffic_regulator['supernode_id'])
    regulator = traffic_regulator[[
        'signal_id', 'lon', 'lat', 'y_pred_rf_final']]

    s = gpd.GeoSeries([Point(x, y)
                      for x, y in zip(regulator['lon'], regulator['lat'])])
    regulator_gpd = gpd.GeoDataFrame(regulator, geometry=s)
    regulator_gpd.crs = {'init': 'epsg:4326'}
    regulator_gpd.to_file(regulator_path, driver="GeoJSON")


def regulator_clipping(boundary_path):
    if regulator_path != '':
        logger.info("==== Loading the processed regulator geojson ===")
        regulator = gpd.read_file(regulator_path)
        city_boundry = gpd.read_file(boundary_path)
        city_boundry = city_boundry.to_crs({'init': 'epsg:4326'})
        logger.info("Started clipping regulator geojson to city boundary......")
        regulator_city = gpd.clip(regulator, city_boundry)
        logger.info(" Finished clipping regulator geojson to city boundary")
        # export data
        logger.info(f"write data to {processed_path}")
        regulator_city.to_file(os.path.join(
            write_directory, f"regulator_{city_name}.geojson"), driver="GeoJSON")
        logger.info(f" #regulators: {len(regulator_city)}")
        logger.info(" ==== Completed regulator processing ====")
        logger.info(
            "-------------------End data transformation-------------------")
    else:
        logger.info("==== No processed regulator path ===")


if __name__ == "__main__":
    if not os.path.exists(gdflinks_path):
        gdf_wholenetwork()

    if not os.path.exists(os.path.join(write_directory, f"boundary_{city_name}.geojson")):
        logger.info(
            " Report is for city, extracting city boundary from the region boundary")
        filter_cityboundary_from_regionboundary(
            regioncities_boundary_path, cityname_in_boundaryfile)
        boundary_path = os.path.join(
            write_directory, f"boundary_{city_name}.geojson")
        network_clipping(boundary_path)

    if not os.path.exists(os.path.join(write_directory, f"citylegs_{city_name}.geojson")):
        legs_city_based_clippedlinks()

    if not os.path.exists(os.path.join(write_directory, f"reclassifylinks_{city_name}.geojson")):
        boundary_path = city_boundary_path
        reclassify_network_clipping(boundary_path)

    if not os.path.exists(regulator_path):
        regulator_preprocessing()

    if not os.path.exists(os.path.join(write_directory, f"regulator_{city_name}.geojson")):
        boundary_path = city_boundary_path
        regulator_clipping(boundary_path)

    logger.info("======= All required base files are present ========")
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
