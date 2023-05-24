import logging
from pathlib import Path
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import shapely.geometry as geom

def set_logger(log_path):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_path, mode="a")
    formatter = logging.Formatter(
        "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(f"Finished logger configuration!")
    return logger

def networkGeom(links,nodes, crs = "epsg:4326"):
    nodes['geom'] = [Point(xy) for xy in zip(nodes.LON, nodes.LAT)]
    gdf_nodes = gpd.GeoDataFrame(nodes, geometry=nodes.geom, crs = crs)
    links['ref_lat'] = links['REF_IN_ID'].map(nodes.set_index('NODE_ID')['LAT'])
    links['ref_long'] = links['REF_IN_ID'].map(nodes.set_index('NODE_ID')['LON'])
    links['nref_lat'] = links['NREF_IN_ID'].map(nodes.set_index('NODE_ID')['LAT'])
    links['nref_long'] = links['NREF_IN_ID'].map(nodes.set_index('NODE_ID')['LON'])
    links['geometry'] = links.apply(lambda x: geom.LineString([(x['ref_long'], x['ref_lat']) , (x['nref_long'], x['nref_lat'])]), axis = 1)
    gdf_links = gpd.GeoDataFrame(links, geometry = links.geometry, crs = crs)
    return gdf_links, gdf_nodes

def generateColumnNames():
    """
    Generates column names for the mobiliti results output.
    """
    result = ['link_id','00:00']
    minc, hourc = 0,0
    for i in range(0,95):
        minc +=1
        if minc % 4 == 0:
            minc = 0
            hourc +=1
        mindigit =  "00" if minc==0 else str(minc*15)
        result.append('%02d'%hourc + ':' + mindigit)
    result.append('unnamed')
    return result

def read_file(path):
    colnames = generateColumnNames()
    file = pd.read_csv(path, sep = '\t',header = None, names =colnames)
    file.drop(file.columns[len(file.columns)-1], axis=1, inplace=True) #dropping the last Nan column
    return file

def results_city_len(flow,links):
    flow_c  = flow.merge(links, left_on = 'link_id', right_on = 'LINK_ID', how = 'left')
    return flow_c

# Filtering flow or speed results for a city and adding link attributes to the flow and speed
def resultscity_filter_len(flow,citylinks):
    flow_sub = flow[flow.link_id.isin(citylinks.LINK_ID)]
    flow_c  = flow_sub.merge(citylinks, left_on = 'link_id', right_on = 'LINK_ID', how = 'left')
    return flow_c

def vmt(flow):
    '''Vehicle Miles Travelled.
    Flow df needs to have the link atrribute length in it'''
    vmt = np.sum(flow.loc[:,"00:00":"23:45"].sum(axis = 1)*15*60*flow.loc[:,'LENGTH(meters)']*0.000621371) #count*length of road VMT
    return np.round(vmt, decimals=0)


def vhd(flow, speed, delaydf = False):
    '''Input: flow and speed df with both having length attribute
       Output: VHD for whole area'''

    d_f = flow.copy()
    d_f.set_index('link_id', inplace = True)
    d_f.loc[:,"00:00":"23:45"] = d_f.loc[:,"00:00":"23:45"]*15*60  #flow to count

    d_time =  speed.copy()
    d_time.set_index('link_id', inplace = True)
    d_time.loc[:,"00:00":"23:45"] = np.reciprocal(d_time.loc[:,"00:00":"23:45"])
    d_time.loc[:, "00:00":"23:45"] = d_time.loc[:,"00:00":"23:45"].mul(d_time['LENGTH(meters)'], axis = 0)   #speed to time (in seconds)

    d_time['tt_free'] = d_time['LENGTH(meters)']/(d_time['SPEED_KPH']*0.277778)  # freeflow tt in seconds
    d_delay = d_time.iloc[:, np.r_[0:96,-1]]
    d_delay = d_delay.sub(d_delay['tt_free'], axis = 0) #delay in seconds
    d_delay[d_delay<0] = 0 #convert negative delays to 0 . Negative delays occur because sometimes speeds are higher in 4th digit in the simulation due to rounding off  numeric error or unit coversion in simulator. 
    #delay multiply by count
    delay_count_df =d_delay.loc[:,"00:00":"23:45"].mul(d_f.loc[:,"00:00":"23:45"]) #vehicle seconds delay

    if delaydf == False:
        return np.round(delay_count_df.sum().sum()/3600 ,decimals=0) #VHD
    else:
        delay_count_df['VHD_link'] = delay_count_df.sum(axis = 1)/3600 # vehicle hours delay for each link
        delay_count_df.reset_index(inplace = True)
        return delay_count_df # hours

def fuel_gallons(fuel_city):
    '''Fuel comsumption.'''

    time = fuel_city.columns[1:97]
    fuel_b = []
    for i in time:
        fuel_b.append(fuel_city[i].sum())
    fuelga = np.sum(fuel_b)*0.264172 #gallons
    return np.round(fuelga, decimals = 0)

def preprocess_legs(legs):
    legs['congestedtt'] = pd.to_datetime(legs['duration (congested)'],errors = 'coerce',format = "%H:%M:%S.%f")
    legs['congested_ttmin'] = legs['congestedtt'].dt.hour*60+ legs['congestedtt'].dt.minute + legs['congestedtt'].dt.second/60
    return legs
