import sys
sys.path.append("general_config")
from load_data import *
import utility as util

logger.info(f" Started script {os.path.basename(__file__)}")
write_directory = os.path.join(processed_path, city_name)


def system_metrics():
    """
    generates summary metrics from flow speed tables.
    """
    logger.info("Loading Mobiliti simulation results...")
    city_links = gpd.read_file(citylinks_path)
    logger.info("Reading in the mobiliti flow files..")
    flow = util.read_file(os.path.join(mobiliti_path, fpath))
    flowcity = flow[flow['link_id'].isin(city_links.LINK_ID)]
    flowcity = util.results_city_len(flowcity, city_links)
    logger.info("Generating VMT and ADT")
    flowcity['vmt'] = (flowcity.loc[:, "00:00":"23:45"].sum(
        axis=1) * 15 * 60 * flowcity.loc[:, 'LENGTH(meters)'] * 0.000621371).astype(int)
    flowcity['adt'] = (flowcity.loc[:, "00:00":"23:45"].sum(
        axis=1) * 15 * 60).astype(int)
    logger.info("Generating system metrics table and adding VMT, ADT")
    system_metrics = city_links.copy()
    system_metrics = system_metrics.merge(
        flowcity[['link_id', 'vmt', 'adt']], left_on='LINK_ID', right_on='link_id', how='left')

    logger.info("Reading in the mobiliti speed files..")
    speed = util.read_file(os.path.join(mobiliti_path, spath))
    speedcity = speed[speed['link_id'].isin(city_links.LINK_ID)]
    speedcity = util.results_city_len(speedcity, city_links)
    logger.info("Generating VHD")
    vhddf = util.vhd(flowcity, speedcity, delaydf=True)  # VHD in hours
    logger.info("Adding VHD to system metrics table")
    system_metrics = system_metrics.merge(
        vhddf[['link_id', 'VHD_link']], left_on='LINK_ID', right_on='link_id', how='left')
    system_metrics.rename(columns={'VHD_link': 'vhd_sec'}, inplace=True)
    system_metrics['vhd_sec'] = system_metrics['vhd_sec'] * \
        3600  # delay in seconds
    system_metrics['vhd_sec'] = system_metrics['vhd_sec'].round(0).astype(int)

    logger.info("Reading in the mobiliti fuel files..")
    fuel = util.read_file(os.path.join(mobiliti_path, fupath))
    fuelcity = fuel[fuel['link_id'].isin(city_links.LINK_ID)]
    fuelcity = util.results_city_len(fuelcity, city_links)
    logger.info("Generating Fuel per link in litres")
    fuelcity['fuel_lit'] = fuelcity.loc[:,
                                        "00:00": "23:45"].sum(axis=1)  # litres
    logger.info("Adding Fuel to system metrics table")
    system_metrics = system_metrics.merge(
        fuelcity[['link_id', 'fuel_lit']], left_on='LINK_ID', right_on='link_id', how='left')
    system_metrics['fuel_lit'] = system_metrics['fuel_lit'].round(
        0).astype(int)

    # write
    logger.info(f"write data to {processed_path}")
    system_metrics.to_file(os.path.join(
        write_directory, f"systemmetrics_{city_name}.geojson"), driver="GeoJSON")
    logger.info(f" # links: {len(city_links)}")


def networktable(report=True):
    if relinkspath != '':
        mToMile = 0.000621371
        reclassifylinks = gpd.read_file(relinkspath)
        city_links = gpd.read_file(citylinks_path)
        links_re_city = pd.merge(city_links, reclassifylinks[['LINK_ID', 'new_classi']], left_on='LINK_ID', right_on='LINK_ID',
                                 how='left')
        links_re = links_re_city.copy()

        networkLen = (links_re['LENGTH(meters)'].sum()
                      * mToMile).astype(int)  # miles

        def lengthMiles(links_re, c): return (
            links_re[links_re['new_classi'] == c]['LENGTH(meters)'].sum() * mToMile).astype(int)

        neighRes, resThouro = lengthMiles(links_re, 'Neighbourhood Residential street'), lengthMiles(
            links_re, 'Residential Throughway')
        neighComm, highway = lengthMiles(
            links_re, 'Neighbourhood Commercial street'), lengthMiles(links_re, 'Highway')

        city_regulator = gpd.read_file(os.path.join(
            config["etl"]["processed_path"], city_name, f"regulator_{city_name}.geojson"))
        traffSignal = len(
            city_regulator[city_regulator['y_pred_rf_final'] == 2]['signal_id'].unique())

        if report == True:
            temp1 = {'Network length (unidirectional miles)': networkLen, 'Length of highway': highway, 'Length of neighbourhood residential street': neighRes,
                     'Length of residential throughway street': resThouro, 'Length of neighbourhood commercial street ': neighComm,
                     'Estimated number of intersections': len(city_regulator['signal_id'].unique()), 'Estimated number of traffic signals': traffSignal}
            networkdf = pd.DataFrame(columns=['Metric', 'Value'])
            for k, v in temp1.items():
                networkdf.loc[networkdf.shape[0]] = [k, v]

            if city_name == 'san_jose':
                # only for sanjose - traffic signal manually add as suggested by Jane's discussion with the city
                networkdf.loc[6, "Value"] = 900

            networkdf.loc[:, "Value"] = networkdf["Value"].map('{:,d}'.format)
            print(networkdf)
            return networkdf.style.hide_index()

        else:
            return networkLen


if __name__ == "__main__":
    system_metrics()
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
