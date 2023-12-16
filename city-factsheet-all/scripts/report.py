import datapane as dp
print("datapane version" , dp.__version__)
import sys
sys.path.append("general_config")
from load_data import *

from system_metrics import networktable
from trafficmetrics_table import systemtraffic_table
from triplegs_metrics import worktrip_destination_heatmap
from high_adt import highestADT
from commute_trips import mean_commute_tt
import text 
import key
# dp.login(token = key.datapane_key)

write_directory = os.path.join(processed_path,city_name, 'figures')

def report():
    """
    Generates datapane report
    """
    print(" Starting to load in files for report...")
    #figures
    vmtpath = os.path.join(write_directory, f"vmt_{city_name}.png")
    vhdpath = os.path.join(write_directory, f"vhd_{city_name}.png")
    fuelpath = os.path.join(write_directory, f"fuel_{city_name}.png")
    adtpath = os.path.join(write_directory, f"adt_{city_name}.png")
    trippurposepath = os.path.join(write_directory, f"trippurpose_{city_name}.png")

    # tripleg_distance_hist = os.path.join(figures_path, f"HistogramofTripDistance_{city_name}.png")
    # tripleg_time_hist = os.path.join(figures_path, f"HistogramofTripTime_{city_name}.png")

    #tables
    print("Generating tables ...")
    networkdf = networktable()
    systemdf, vmtpercapita = systemtraffic_table()

    #main blocks
    print("Generating work trip travel time ...")
    worktrip_tt = mean_commute_tt(trips_start_work_city_path)

    #heatMap
    print("Generating Heatmaps ...")
    workHeatmap = worktrip_destination_heatmap()
    adtLocation, adttable = highestADT()
    #truckadtLocation, truckadttable = truckHighestADT()

    #blocks
    legs_block = [dp.Media(file = trippurposepath), workHeatmap]
    #legs_block = [dp.Media(file = tripleg_distance_hist),dp.Media(file = tripleg_time_hist)]

    #bignumbers
    vmtpercapita_block = dp.BigNumber(heading= "VMT per capita", value= vmtpercapita, is_upward_change=True)
    worktriptt_block = dp.BigNumber(heading="Mean work travel time (min)", value=worktrip_tt)

    #Report
    report_content = dp.View(
        dp.Group(dp.HTML(text.cityStat),vmtpercapita_block,worktriptt_block, columns=3),
        dp.HTML(text.networkStat),
        dp.Group(dp.Table(networkdf),dp.Table(systemdf),columns = 2),
        dp.HTML(text.systemStat),
        dp.Group(dp.Media(file = adtpath), dp.Media(file = vhdpath),dp.Media(file = fuelpath), columns = 3),
        dp.HTML(text.adtStat),
        dp.Group(dp.Plot(adtLocation), dp.Table(adttable), columns = 2 ),
        dp.HTML(text.trips),
        dp.Group(columns = 2, blocks = legs_block),
        #dp.Group(dp.HTML(text.truck),dp.HTML(text.truckHighest),columns = 2 ),
        #dp.Group(dp.Media(file = truck_adt),dp.Plot(truckadtLocation), columns = 2),
        #dp.Group(dp.Media(file = truck_vmtbar),dp.Table(truckadttable), columns = 2),
        dp.HTML(text.aboutMobiliti)
        )
    dp.save_report(report_content, path = f'Smart Cities Research Center: {city_name_report}.html')

    
    # dp.upload_report(report_content, name = f'Smart Cities Research Center: {city_name_report}', 
    #                  publicly_visible=True) #formatting = dp.Formatting(width = dp.Formatting.width.FULL, bg_color = "#FFF", accent_color = "#4E46E5", text_alignment = dp.Formatting.text_alignment.JUSTIFY,  
    #                                                                    #font = dp.Formatting.font.DEFAULT, light_prose = False))

if __name__ == "__main__":
    report()
