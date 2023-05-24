import sys
sys.path.append("general_config")
from load_data import *
import utility as util

logger.info(f" Started script {os.path.basename(__file__)}")
write_directory = os.path.join(processed_path, city_name, 'figures')


def truck_count_city():
    city_links = gpd.read_file(citylinks_path)
    truck_filepaths = [truck_code_one, truck_code_two, truck_code_three]
    truckcount_df = pd.DataFrame()
    for tpath in truck_filepaths:
        if tpath != "":
            counts = util.read_file(tpath)
            truckcount_df = truckcount_df.append(counts, sort=False)

    truckcount_city = truckcount_df[truckcount_df['link_id'].isin(city_links.LINK_ID)]
    truckcount_city = util.results_city_len(truckcount_city, city_links)
    return truckcount_city


def truck_vmt():
    if is_truck == 'yes':
        truckcount_city = truck_count_city()
        truck_vmt = np.sum(truckcount_city.loc[:, "00:00":"23:45"].sum(axis=1) * truckcount_city.loc[:, 'LENGTH(meters)'] * 0.000621371)  # count*length of road VMT
        truck_vmt = np.round(truck_vmt, decimals=0)
        return truck_vmt
    else:
        return 0  # no truck vmt


def truck_adt_map():
    truckcount_city = truck_count_city()
    truckcount_city['adt'] = 0
    pd.options.mode.chained_assignment = None
    truckcount_city.loc[:, 'adt'] = truckcount_city.loc[:, "00:00":"23:45"].sum(axis=1)

    city_links = gpd.read_file(citylinks_path)
    truckgpd = city_links.copy()
    truckgpd = truckgpd.merge(truckcount_city[['link_id', 'adt']], left_on='LINK_ID', right_on='link_id', how='left')

    city_boundary = gpd.read_file(city_boundary_path)

    logger.info("Plotting ADT")
    south, north = [min(truckgpd.ref_lat) - 0.015, max(truckgpd.ref_lat) + 0.015]
    west, east = [min(truckgpd.ref_long) - 0.015, max(truckgpd.ref_long) + 0.015]
    width, height = 15, 14

    filter1 = truckgpd[(truckgpd['adt'] > 50)]
    fig1, (ax) = plt.subplots(1, 1, figsize=(width, height))
    ax.axis([west, east, south, north])
    modified_cmap = mpl.cm.OrRd(np.linspace(0, 1, 20))
    modified_cmap = mpl.colors.ListedColormap(modified_cmap[8:, :-1])
    filter1.plot(ax=ax, column="adt", linewidth=1, cmap=modified_cmap, scheme="quantiles", legend=True)
    city_boundary.boundary.plot(ax=ax, color='grey', linewidth=1.5)
    ctx.add_basemap(ax, zoom=13, crs=filter1.crs.to_string(), source=ctx.providers.CartoDB.Positron)
    ax.set_axis_off()
    fig1.savefig(os.path.join(write_directory, f"truckadt_{city_name}.png"), bbox_inches='tight')
    logger.info("Completed truck adt plot")


def truckVMTBar():
    truckcount_city = truck_count_city()

    # converting count to flow to use in the vmt function
    truckcount_city.iloc[:, 1:97] = truckcount_city.iloc[:, 1:97] / 15 / 60

    def vmt_func(flow, t1, t2): return np.sum(flow.loc[:, t1:t2].sum(axis=1) * 15 * 60 * flow.loc[:, 'LENGTH(meters)'] * 0.000621371)

    time_ranges = [("early_morning", "00:00", "05:45"),
                   ("morning", "06:00", "10:45"),
                   ("midday", "11:00", "14:45"),
                   ("evening", "15:00", "18:45"),
                   ("late_evening", "19:00", "23:45")]
    truck_vmt_time = {time_range[0]: int(vmt_func(truckcount_city, time_range[1], time_range[2]) / 1000)
                      for time_range in time_ranges}

    width, height = 5, 3
    fig1, (ax) = plt.subplots(1, 1, figsize=(width, height))
    t1 = plt.bar(*zip(*truck_vmt_time.items()), width=0.5, align='center', figure=fig1, color='brown')
    plt.xlabel("Time of Day")
    plt.ylabel("VMT (in thousands)")
    plt.title("Truck VMT")
    fig1.savefig(os.path.join(write_directory, f"truckvmt_{city_name}.png"), bbox_inches='tight')


if __name__ == "__main__":
    if is_truck == 'yes':
        truck_adt_map()
        truckVMTBar()

    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
