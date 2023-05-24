import sys
sys.path.append("general_config")
from load_data import *
import utility as util

from commute_trips import mean_commute_tt
from communities_concern import coc_traffic_metrics, coc_bg, coc_networkmiles
from triplegs_metrics import worktrip_destination_heatmap
import text
import key
from high_adt import highestADT
from trafficmetrics_table import systemtraffic_table
from system_metrics import networktable

import datapane as dp
print("datapane version", dp.__version__)

dp.login(token=key.datapane_key)
write_directory = os.path.join(processed_path, city_name, 'figures')


def report():
    """
    Generates datapane report
    """
    # figures
    vmtpath = os.path.join(write_directory, f"vmt_{city_name}.png")
    vhdpath = os.path.join(write_directory, f"vhd_{city_name}.png")
    fuelpath = os.path.join(write_directory, f"fuel_{city_name}.png")
    adtpath = os.path.join(write_directory, f"adt_{city_name}.png")

    coc_ct_city = os.path.join(write_directory, f"coc_{city_name}.png")
    truck_adt = os.path.join(write_directory, f"truckadt_{city_name}.png")
    truck_vmtbar = os.path.join(write_directory, f"truckvmt_{city_name}.png")
    reclasspath = os.path.join(
        write_directory, f"barplot_reclassify_{city_name}.png")
    trippurposepath = os.path.join(
        write_directory, f"trippurpose_{city_name}.png")

    # tables
    networkdf = networktable()
    systemdf, vmtpercapita = systemtraffic_table()
    cocdf = coc_traffic_metrics()

    # heatMap
    print("Generating Heatmaps ...")
    workHeatmap = worktrip_destination_heatmap()
    adtLocation, adttable = highestADT()
    worktrip_tt = mean_commute_tt(trips_start_work_city_path)

    # coc criteria to plot
    cocbg = coc_bg()  # number of coc block Groups
    coc_network = coc_networkmiles()  # percentage
    if cocbg == 0 or coc_network <= 2:
        coc_block = []
        coc_val = "."  # Text data is set to None
    else:
        coc_block = [dp.Media(file=coc_ct_city), dp.Table(cocdf)]
        coc_val = text.coc

    # blocks
    legs_block = [dp.Media(file=trippurposepath), dp.Plot(workHeatmap)]

    # bignumbers
    vmtpercapita_block = dp.BigNumber(
        heading="VMT per capita", value=vmtpercapita, is_upward_change=True)
    worktriptt_block = dp.BigNumber(
        heading="Mean work travel time (min)", value=worktrip_tt)

    dp.enable_logging()

    # Report
    report_content = dp.View(
        dp.Group(dp.HTML(text.cityStat), vmtpercapita_block,
                 worktriptt_block, columns=3),
        dp.HTML(text.networkStat),
        dp.Group(dp.Table(networkdf), dp.Table(systemdf),
                 dp.Media(file=reclasspath), columns=3),
        dp.HTML(text.systemStat),
        dp.Group(dp.Media(file=adtpath), dp.Media(file=vhdpath),
                 dp.Media(file=fuelpath), columns=3),
        dp.HTML(text.adtStat),
        dp.Group(dp.Plot(adtLocation), dp.Table(adttable), columns=2),
        dp.HTML(text.truck),
        dp.Group(dp.Media(file=truck_adt), dp.Media(
            file=truck_vmtbar), columns=2),
        dp.HTML(text.trips),
        dp.Group(blocks=legs_block, columns=2),
        dp.HTML(coc_val),
        dp.Group(blocks=coc_block, columns=2),
        dp.HTML(text.aboutMobiliti)
    )

    dp.upload_report(report_content, name=f'Smart Cities Research Center: {city_name_report}',
                     publicly_visible=True)


if __name__ == "__main__":
    report()
