import sys
sys.path.append("general_config")
from load_data import *

logger.info(f" Started script {os.path.basename(__file__)}")
write_directory = os.path.join(processed_path, city_name, 'figures')


def visuals():
    """
    Main function that trains & persists model based on training set
    Args:
        config_file [str]: path to config file
    Returns:
        None
    """
    logger.info("Reading in system metrics file")
    system_metric = gpd.read_file(systemmetric_path)
    logger.info("Reading in boundary file")

    city_boundary = gpd.read_file(city_boundary_path)

    logger.info("Plotting VMT")
    south, north = [system_metric.ref_lat.min() - 0.015, system_metric.ref_lat.max() + 0.015]
    west, east = [system_metric.ref_long.min() - 0.015, system_metric.ref_long.max() + 0.015]
    width, height = 15, 10

    if 'vmt' in system_metric.columns:
        filter1 = system_metric.query('vmt > 1')
        fig1, (ax) = plt.subplots(1, 1, figsize=(width, height))
        ax.axis([west, east, south, north])
        filter1.plot(ax=ax, column="vmt", linewidth=1, cmap='YlOrRd', scheme="quantiles", legend=True)
        city_boundary.boundary.plot(ax=ax, color='grey', linewidth=1.5)
        ctx.add_basemap(ax, zoom=13, crs=filter1.crs.to_string(), source=ctx.providers.CartoDB.Positron)
        ax.set_axis_off()
        logger.info("writing the image to directory")
        fig1.savefig(os.path.join(write_directory, f"vmt_{city_name}.png"), bbox_inches='tight')
    else:
        logger.info(f"vmt column not found in the {systemmetric_path} file")

    logger.info("Plotting ADT")
    if 'adt' in system_metric.columns:
        filter1 = system_metric.query('adt > 1')
        fig1, (ax) = plt.subplots(1, 1, figsize=(width, height))
        ax.axis([west, east, south, north])
        # modified_cmap = mpl.cm.BuGn(np.linspace(0,1,20))
        # modified_cmap = mpl.colors.ListedColormap(modified_cmap[8:,:-1])
        filter1.plot(ax=ax, column="adt", linewidth=1, cmap='YlOrRd', scheme="quantiles", legend=True)
        city_boundary.boundary.plot(ax=ax, color='grey', linewidth=1.5)
        ctx.add_basemap(ax, zoom=13, crs=filter1.crs.to_string(), source=ctx.providers.CartoDB.Positron)
        ax.set_axis_off()
        logger.info("writing the image to directory")
        fig1.savefig(os.path.join(write_directory, f"adt_{city_name}.png"), bbox_inches='tight')
    else:
        logger.info(f"adt column not found in the {systemmetric_path} file")

    logger.info("Plotting VHD")
    if 'vhd_sec' in system_metric.columns:
        filter1 = system_metric.query('vhd_sec > 30')  # atleast half minute delay a day
        fig1, (ax) = plt.subplots(1, 1, figsize=(width, height))
        ax.axis([west, east, south, north])
        modified_cmap = mpl.cm.YlGnBu(np.linspace(0, 1, 20))
        modified_cmap = mpl.colors.ListedColormap(modified_cmap[8:, :-1])
        filter1.plot(ax=ax, column="vhd_sec", linewidth=1, cmap=modified_cmap, scheme="quantiles", legend=True)
        city_boundary.boundary.plot(ax=ax, color='grey', linewidth=1.5)
        ctx.add_basemap(ax, zoom=13, crs=filter1.crs.to_string(), source=ctx.providers.CartoDB.Positron)
        ax.set_axis_off()
        logger.info("writing the image to directory")
        fig1.savefig(os.path.join(write_directory, f"vhd_{city_name}.png"), bbox_inches='tight')
    else:
        logger.info(f"vhd column not found in the {systemmetric_path} file")

    logger.info("Plotting Fuel")
    if 'fuel_lit' in system_metric.columns:
        filter1 = system_metric.query('fuel_lit > 0')
        fig1, (ax) = plt.subplots(1, 1, figsize=(width, height))
        ax.axis([west, east, south, north])
        filter1.plot(ax=ax, column='fuel_lit', linewidth=1, cmap='PuRd', scheme="quantiles", legend=True)
        city_boundary.boundary.plot(ax=ax, color='grey', linewidth=1.5)
        ctx.add_basemap(ax, zoom=13, crs=filter1.crs.to_string(), source=ctx.providers.CartoDB.Positron)
        ax.set_axis_off()
        logger.info("writing the image to directory")
        fig1.savefig(os.path.join(write_directory, f"fuel_{city_name}.png"), bbox_inches='tight')
    else:
        logger.info(f"fuel column not found in the {systemmetric_path} file")

    logger.info("Completed 4 plots")


if __name__ == "__main__":
    visuals()
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
