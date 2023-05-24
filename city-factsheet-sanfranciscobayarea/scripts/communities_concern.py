import sys
sys.path.append("general_config")
from load_data import *

from system_metrics import networktable
from trafficmetrics_table import systemtraffic_table
import matplotlib.patches as mpatches
import utility as util

logger.info(f" Started script {os.path.basename(__file__)}")
write_directory = os.path.join(processed_path, city_name, 'figures')


def coc_map():
    if bayarea_coc_links != '':
        coc_shapefile = gpd.read_file(bayarea_coc_shapefile)
        city_boundary = gpd.read_file(city_boundary_path)
        coc_city = gpd.clip(coc_shapefile, city_boundary)

        # to choose figure boundary limits
        city_links = gpd.read_file(citylinks_path)
        south, north = [min(city_links.ref_lat) - 0.015,
                        max(city_links.ref_lat) + 0.015]
        west, east = [min(city_links.ref_long) - 0.015,
                      max(city_links.ref_long) + 0.015]
        width, height = 15, 14

        fig1, (ax) = plt.subplots(1, 1, figsize=(width, height))
        ax.axis([west, east, south, north])

        colors = {'High': '#FFD700', 'Higher': '#F79306',
                  'Highest': '#FF6347', 'NA': 'white'}
        high_patch = mpatches.Patch(color='#FFD700', label=' High')
        higher_patch = mpatches.Patch(color='#F79306', label='Higher')
        highest_patch = mpatches.Patch(color='#FF6347', label='Highest')

        coc_city.plot(ax=ax, color=coc_city['coc_class'].apply(
            lambda x: colors[x]), alpha=0.7, legend=True)
        city_boundary.boundary.plot(ax=ax, color='grey', linewidth=1.5)
        ctx.add_basemap(ax, zoom=13, crs=coc_city.crs.to_string(),
                        source=ctx.providers.CartoDB.Positron)
        ax.set_axis_off()
        ax.legend(handles=[high_patch, higher_patch, highest_patch])
        fig1.savefig(os.path.join(write_directory,
                     f"coc_{city_name}.png"), bbox_inches='tight')
        ld.logger.info("Completed writing the image to png")


def coc_bg():
    """ Number of  Communities of Concern Block Groups in a city"""
    if bayarea_coc_links != '':
        coc_shapefile = gpd.read_file(bayarea_coc_shapefile)
        city_boundary = gpd.read_file(city_boundary_path)
        coc_city = gpd.clip(coc_shapefile, city_boundary)
        cocbg_number = len(
            coc_city[coc_city['coc_class'].isin(['High', 'Higher', 'Highest'])])
        return cocbg_number


def coc_networkmiles():
    """Length of the network within Communities of Concern """
    if bayarea_coc_links != '':
        coclinks = pd.read_csv(bayarea_coc_links)
        city_links = gpd.read_file(citylinks_path)
        citycoclinks = coclinks[coclinks['LINK_ID'].isin(
            city_links['LINK_ID'])]
        citycoclinks = citycoclinks[citycoclinks['coc_class'].isin(
            ['High', 'Higher', 'Highest'])]
        citycoclinks = pd.merge(citycoclinks, city_links[[
                                'LINK_ID', 'LENGTH(meters)']], left_on='LINK_ID', right_on='LINK_ID', how='left')
        # percentage
        return int(citycoclinks['LENGTH(meters)'].sum() / city_links['LENGTH(meters)'].sum() * 100)


def coc_traffic_metrics():
    if bayarea_coc_links != '':
        coclinks = pd.read_csv(bayarea_coc_links)
        city_links = gpd.read_file(citylinks_path)
        logger.info("Total links in city", len(city_links))
        citycoclinks = coclinks[coclinks['LINK_ID'].isin(
            city_links['LINK_ID'])]
        citycoclinks = citycoclinks[citycoclinks['coc_class'].isin(
            ['High', 'Higher', 'Highest'])]
        logger.info("CoC links in city", len(citycoclinks))

        flow = util.read_file(os.path.join(mobiliti_path, fpath))
        flowcoc = flow[flow['link_id'].isin(citycoclinks.LINK_ID)]
        flowcoc = util.results_city_len(flowcoc, city_links)

        speed = util.read_file(os.path.join(mobiliti_path, spath))
        speedcoc = speed[speed['link_id'].isin(citycoclinks.LINK_ID)]
        speedcoc = util.results_city_len(speedcoc, city_links)

        fuel = util.read_file(os.path.join(mobiliti_path, fupath))
        fuelcoc = fuel[fuel['link_id'].isin(citycoclinks.LINK_ID)]
        fuelcoc = util.results_city_len(fuelcoc, city_links)

        cocVmt, cocVhd, cocFuel = util.vmt(flowcoc), util.vhd(
            flowcoc, speedcoc), util.fuel_gallons(fuelcoc)
        logger.info("COC Metrics vmt, vhd, fuel", cocVmt, cocVhd, cocFuel)

        # Whole city VMT, VHD, Fuet for rayio comparison
        cityVmt, cityVhd, cityFuel = systemtraffic_table(report=False)
        networkLen = networktable(report=False)  # miles

        # Coc Dataframe
        mToMile = 0.000621371
        coc_df = pd.DataFrame(columns=['Metric', '% Share'])
        temp2 = {'Network Miles': int(flowcoc['LENGTH(meters)'].sum() * mToMile * 100 / networkLen),
                 'VMT': int(cocVmt / cityVmt * 100), 'VHD': int(cocVhd / cityVhd * 100), 'Fuel': int(cocFuel / cityFuel * 100)}
        for k, v in temp2.items():
            coc_df.loc[coc_df.shape[0]] = [k, v]

        print(coc_df)
        return coc_df.style.hide_index()


if __name__ == "__main__":
    coc_map()
    # coc_bg()
    # coc_networkmiles()
    # coc_traffic_metrics()

    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
