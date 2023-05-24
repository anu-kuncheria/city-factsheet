import sys
sys.path.append("general_config")
from load_data import *
from utility import set_logger,read_file,results_city_len, vhd

logger.info(f" Started script {os.path.basename(__file__)}")
write_directory = os.path.join(processed_path,city_name)

def system_metrics():
    """
    generates summary metrics from flow speed tables.
    """
    logger.info("Loading in processed city links ...")
    city_links = gpd.read_file(citylinks_path)
    logger.info("Reading in the mobiliti flow files..")
    flow = read_file(os.path.join(mobiliti_path, fpath))
    flowcity = flow[flow['link_id'].isin(city_links.LINK_ID)]
    flowcity = results_city_len(flowcity,city_links)
    logger.info("Generating VMT and ADT")
    flowcity['vmt'] = (flowcity.loc[:,"00:00":"23:45"].sum(axis = 1)*15*60*flowcity.loc[:,'LENGTH(meters)']*0.000621371).astype(int)
    flowcity['adt'] = (flowcity.loc[:,"00:00":"23:45"].sum(axis = 1)*15*60).astype(int)
    logger.info("Generating system metrics table and adding VMT, ADT")
    system_metrics = city_links.copy()
    system_metrics = system_metrics.merge(flowcity[['link_id','vmt','adt']], left_on = 'LINK_ID', right_on = 'link_id', how = 'right') #not every link in the city will have row in flow speed tables - new update
    #print(len(system_metrics))

    logger.info("Reading in the mobiliti speed files..")
    speed = read_file(os.path.join(mobiliti_path, spath))
    speedcity = speed[speed['link_id'].isin(city_links.LINK_ID)]
    speedcity = results_city_len(speedcity,city_links)
    logger.info("Generating VHD")
    vhddf = vhd(flowcity, speedcity, delaydf = True) # VHD in hours
    #print(vhddf.isnull().sum())

    logger.info("Adding VHD to system metrics table")
    system_metrics = system_metrics.merge(vhddf[['link_id','VHD_link']], left_on = 'LINK_ID', right_on = 'link_id', how = 'left')
    system_metrics.rename(columns = {'VHD_link':'vhd_sec'}, inplace = True)
    system_metrics['vhd_sec'] = system_metrics['vhd_sec']*3600 # delay in seconds
    system_metrics['vhd_sec'] = system_metrics['vhd_sec'].round(0).astype(int)

    logger.info("Reading in the mobiliti fuel files..")
    fuel = read_file(os.path.join(mobiliti_path, fupath))
    fuelcity = fuel[fuel['link_id'].isin(city_links.LINK_ID)]
    fuelcity = results_city_len(fuelcity,city_links)
    logger.info("Generating Fuel per link in litres")
    fuelcity['fuel_lit'] = fuelcity.loc[:, "00:00": "23:45"].sum(axis = 1)  # litres
    logger.info("Adding Fuel to system metrics table")
    system_metrics = system_metrics.merge(fuelcity[['link_id','fuel_lit']], left_on = 'LINK_ID', right_on = 'link_id', how = 'left')
    system_metrics['fuel_lit'] = system_metrics['fuel_lit'].round(0).astype(int)

    logger.info(f"write data to {processed_path}")
    system_metrics.to_file(os.path.join(write_directory, f"systemmetrics_{city_name}.geojson"),driver="GeoJSON")
    logger.info(f" # links: {len(city_links)}")
    logger.info("Completed system_metrics")

def networktable():
    mToMile = 0.000621371
    city_links = gpd.read_file(citylinks_path)
    networkLen = (city_links['LENGTH(meters)'].sum()*mToMile).astype(int) #miles
    lengthMiles = lambda city_links,c: (city_links[city_links['FUNC_CLASS'] == c]['LENGTH(meters)'].sum()*mToMile).astype(int)

    fc1, fc2,fc3 = lengthMiles(city_links, 1), lengthMiles(city_links, 2), lengthMiles(city_links, 3)
    fc4,fc5 = lengthMiles(city_links, 4), lengthMiles(city_links, 5)

    temp1 = {'Network length (unidirectional miles)':networkLen, 
             'Length of FC1 (high volume and maximum speed traffic movement)':fc1,
             'Length of FC2 (high volume and high speed traffic movement)':fc2,
        'Length of FC3 (high volume traffic movement)': fc3,
    'Length of FC4 (high volume and moderate speed traffic movement)':fc4 ,
    'Length of FC5 (low volume and low speed traffic movement) ': fc5}
    
    networkdf = pd.DataFrame(columns = ['Metric', 'Value'])
    for k, v in temp1.items():
        networkdf.loc[networkdf.shape[0]] = [k, v]
    
    networkdf.loc[:, "Value"] = networkdf["Value"].map('{:,d}'.format)
    return networkdf.style.hide_index()

if __name__ == "__main__":
    system_metrics()
    
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
