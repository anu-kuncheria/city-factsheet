import sys
sys.path.append("general_config")
from load_data import *
from utility import set_logger,networkGeom

logger = set_logger(os.path.join(log_path, city_name,'log', "legs_histogram.log"))
logger.info(f"Load config from {config_file}")
logger.info(f" city_name specified in config is {city_name}")

write_directory = os.path.join(processed_path,city_name, 'figures')

def p95(s):
    return np.percentile(s, 95)

def trip_metrics_plot(df,column, unitconversion, xlabel = '', title = '',processed_path = ''):
    fig, ax = plt.subplots(figsize = (10,8))
    p95value = p95(df[column])
    plt.hist(df[df[column]< p95value][column]*unitconversion, bins = 20)
    plt.title(title)
    plt.xlabel(xlabel)
    titlenospace = title.replace(" ","")
    plt.savefig(processed_path /"{}_{}.png".format(titlenospace,city_name)))


def legs_metrics_plot():
    """
    All trips that start or end in a city
    """
    legs =  pd.read_csv(raw_legs_path, sep = '\t')
    city_links = gpd.read_file(citylinks_path)
    citynodeslist = set(list(city_links['REF_IN_ID'].values) + list(city_links['NREF_IN_ID'].values))
    legs_start_end_city = legs[(legs['start node'].isin(citynodeslist)) | (legs['end node'].isin(citynodeslist))]
    legs_start_end_city_processed = preprocess_legs(legs_start_end_city)

    trip_metrics_plot(df =legs_start_end_city_processed,column = 'total distance (m)', unitconversion = 0.000621371 , xlabel = "Trip Distance (miles)", title = "Histogram of Trip Distance",
    processed_path = processed_path )

    trip_metrics_plot(df = legs_start_end_city_processed,column = 'congested_ttmin', unitconversion = 1 , xlabel = " Trip Time (minutes)", title = "Histogram of Trip Time",
    processed_path = processed_path )


if __name__ == '__main__':
    legs_metrics_plot()
