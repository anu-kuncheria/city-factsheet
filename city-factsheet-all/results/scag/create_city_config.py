import geopandas as gpd
import os
import yaml

import sys
sys.path.append("general_config")
from load_data import regioncities_boundary_path

region_boundary = gpd.read_file(regioncities_boundary_path)

for city in region_boundary['city'].unique():
    os.mkdir(os.path.join('city_config', city))

    # report name
    if len(city.split('_')) > 1:
        reportname = " ".join([city.split('_')[i].capitalize() for i in range(len(city.split('_')))])
    else:
        reportname = str(city).capitalize()

    # yaml data
    data = {
        'etl': {
            'city_name': str(city),
            'city_name_report': reportname,
            'regionboundryfile_cityname': city}
    }

    # Write the YAML file
    file_name = 'city_config.yaml'
    file_path = os.path.join(os.path.join('city_config', city), file_name)
    with open(file_path, 'w') as file:
        yaml.dump(data, file)
