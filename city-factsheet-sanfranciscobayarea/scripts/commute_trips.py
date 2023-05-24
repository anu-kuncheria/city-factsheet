import sys
sys.path.append("general_config")
from load_data import *

import utility as util
logger.info(f" Started script {os.path.basename(__file__)}")
write_directory = os.path.join(processed_path, city_name)


def legs_start_work():
    cols = ['leg id', 'purpose', 'start node',
            'end node', 'duration (congested)']
    legs = pd.read_csv(raw_legs_path, sep='\t', usecols=cols)

    logger.info(
        "==== Loading the clipped city links to get all nodes in a city ===")
    city_links = gpd.read_file(citylinks_path)
    citynodeslist = set(
        list(city_links['REF_IN_ID'].values) + list(city_links['NREF_IN_ID'].values))

    logger.info("==== Filtering legs based on city nodes ===")
    legs_start = legs[(legs['start node'].isin(citynodeslist))]

    logger.info("==== Filtering work trips ===")
    legs_work_start = legs_start.query('purpose == 1')

    logger.info("==== Converting congested tt to minutes ===")
    legs_work_start = preprocess_legs(legs_work_start)

    legs_start.to_csv(os.path.join(
        write_directory, f"legs_start_{city_name}.csv"), index=False)
    legs_work_start.to_csv(os.path.join(
        write_directory, f"legs_start_work_{city_name}.csv"), index=False)


# main
if not os.path.exists(trips_start_city_path):
    legs_start_work()


def trips_start(trips_start_city_path):
    legs_start = pd.read_csv(trips_start_city_path)
    return len(legs_start)


def mean_commute_tt(trips_start_work_city_path):
    legs_work_start = pd.read_csv(trips_start_work_city_path)
    mean_worktrip_minutes = np.round(
        legs_work_start['congested_ttmin'].mean(), decimals=1)
    return mean_worktrip_minutes


logger.info(f" === Completed script {os.path.basename(__file__)} ====")
