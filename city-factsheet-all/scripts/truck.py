import sys
sys.path.append("general_config")
from load_data import *
from utility import read_file, results_city_len, vmt

logger.info(f" Started script {os.path.basename(__file__)}")

write_directory = os.path.join(processed_path,city_name, 'figures')

def truck_vmt():
    if is_truck == 'yes':
        city_links = gpd.read_file(citylinks_path)

        truck_filepaths = [truck_code_one,truck_code_two,truck_code_three]
        truckcount_df = pd.DataFrame()
        for path in truck_filepaths:
            counts = read_file(path)
            truckcount_df = truckcount_df.append(counts, sort=False)

        truckcount_city = truckcount_df[truckcount_df['link_id'].isin(city_links.LINK_ID)]
        truckcount_city = results_city_len(truckcount_city,city_links)
        truck_vmt = np.sum(truckcount_city.loc[:,"00:00":"23:45"].sum(axis = 1) * truckcount_city.loc[:,'LENGTH(meters)']*0.000621371) #count*length of road VMT
        truck_vmt = np.round(truck_vmt, decimals=0)
        return truck_vmt
    else:
        return 0 #no truck vmt

if __name__ == "__main__":
    truck_vmt()
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")

