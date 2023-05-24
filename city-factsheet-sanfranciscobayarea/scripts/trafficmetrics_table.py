import sys
sys.path.append("general_config")
from load_data import *
import utility as util
from truck import truck_vmt

logger.info(f" Started script {os.path.basename(__file__)}")


def systemtraffic_table(report=True):
    city_links = gpd.read_file(citylinks_path)
    flow = util.read_file(os.path.join(mobiliti_path, fpath))
    speed = util.read_file(os.path.join(mobiliti_path, spath))
    fuel = util.read_file(os.path.join(mobiliti_path, fupath))

    # whole city
    flowcity = flow[flow['link_id'].isin(city_links.LINK_ID)]
    flowcity = util.results_city_len(flowcity, city_links)
    speedcity = speed[speed['link_id'].isin(city_links.LINK_ID)]
    speedcity = util.results_city_len(speedcity, city_links)
    fuelcity = fuel[fuel['link_id'].isin(city_links.LINK_ID)]
    fuelcity = util.results_city_len(fuelcity, city_links)

    cityVmt, cityVhd, cityFuel = util.vmt(flowcity), util.vhd(flowcity, speedcity), util.fuel_gallons(fuelcity)

    if report == False:
        # to use inside the communities of concern script
        return cityVmt, cityVhd, cityFuel

    else:
        truckVmt = truck_vmt()

        co2pergallon = 8887
        automobileVmt = cityVmt - truckVmt

        # city pop
        citystat_df = pd.read_csv(citystat_path)
        pop = int(citystat_df[citystat_df['city'] == city_name]['population'].values[0])

        # System metrics df
        systemdf = pd.DataFrame(columns=['Metric', 'Value'])
        data = {'Total VMT(thousand miles)': int(cityVmt / 1000), 'Automobile VMT(thousand miles)': int(automobileVmt / 1000), 'Total VHD(hours)': int(
            cityVhd), 'Total Fuel(thousand gallons)': int(cityFuel / 1000), 'Total Emissions (million gCo2)': int(cityFuel * co2pergallon / 1000000)}
        for k, v in data.items():
            systemdf.loc[systemdf.shape[0]] = [k, v]
        systemdf.loc[:, "Value"] = systemdf["Value"].map('{:,d}'.format)
        print(systemdf)
        return systemdf.style.hide_index(), int(automobileVmt / pop)


if __name__ == "__main__":
    systemtraffic_table()
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
