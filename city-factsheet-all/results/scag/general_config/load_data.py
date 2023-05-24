import os
import sys
from pathlib import Path

import logging
import yaml

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import shapely.geometry as geom

import matplotlib.pyplot as plt
import matplotlib as mpl
import contextily as ctx
import mapclassify
import folium
from folium import plugins
import sys

from utility import set_logger

config_file = "general_config/general_config.yaml"
print("Config file loaded is", config_file)
a_yaml_file = open(config_file)
config = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

cityconfigpath = sys.argv[1]
city_config_file = os.path.join(cityconfigpath, "city_config.yaml")
print("City specific config file loaded is", city_config_file)
a_yaml_file = open(city_config_file)
city_config = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

region_name = config["etl"]["region"]
city_name = city_config["etl"]["city_name"]
processed_path = Path(config["etl"]["processed_path"])
log_path = config["etl"]["log_path"]

if not os.path.exists(os.path.join(processed_path,city_name)):
    os.mkdir(os.path.join(processed_path,city_name))

if not os.path.exists(os.path.join(processed_path,city_name, 'figures')):
    os.mkdir(os.path.join(processed_path,city_name, 'figures'))

if not os.path.exists(os.path.join(log_path, city_name,'log')):
    os.mkdir(os.path.join(log_path, city_name,'log'))

logger = set_logger(os.path.join(log_path, city_name,'log', "factsheet.log"))

taz_boundry_file = config["etl"]["taz_boundary_path"]
regionboundary_path = config["etl"]["region_boundary_path"]
cityname_in_boundaryfile = city_config["etl"]["regionboundryfile_cityname"]

links_path = os.path.join(config["etl"]["network_path"], config["etl"]["city_links"])
nodes_path = os.path.join(config["etl"]["network_path"], config["etl"]["city_nodes"])
raw_legs_path = config['etl']["raw_legs_path"]
gdflinks_path = config['etl']["gdf_links_path"]
gdflegs_path = config['etl']["gdf_legs_path"]

mobiliti_path = config["system_metrics"]["mobiliti_path"]
fpath = config["system_metrics"]["fpath"]
spath = config["system_metrics"]["spath"]
fupath = config["system_metrics"]["fupath"]

#extracted using etl.py script
city_boundary_path = os.path.join( config["etl"]["processed_path"], city_name, f"boundary_{city_name}.geojson")
citylinks_path = os.path.join(config["etl"]["processed_path"], city_name, f"citylinks_{city_name}.geojson")
citylegs_path = os.path.join(config["etl"]["processed_path"], city_name, f"citylegs_{city_name}.geojson")

systemmetric_path = os.path.join(config["etl"]["processed_path"], city_name, f"systemmetrics_{city_name}.geojson")

city_name_report = city_config["etl"]["city_name_report"]
citystat_path = config["text"]["citystat_path"]

#truck
is_truck = config["truck"]["truck_demand"]
truck_code_one = os.path.join(config["system_metrics"]["mobiliti_path"], config["truck"]["truckcountpath_1"])
truck_code_two = os.path.join(config["system_metrics"]["mobiliti_path"], config["truck"]["truckcountpath_2"])
truck_code_three = os.path.join(config["system_metrics"]["mobiliti_path"], config["truck"]["truckcountpath_3"])

#commute trips
trips_start_city_path = os.path.join( config["etl"]["processed_path"], city_name, f"legs_start_{city_name}.csv")
trips_start_work_city_path = os.path.join( config["etl"]["processed_path"], city_name, f"legs_start_work_{city_name}.csv")

  

  


