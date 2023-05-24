set -e  

for cityname in pasadena ; do
    echo "======= Running ${cityname}======="
    python3 ../../scripts/etl.py "$(pwd)/city_config/$cityname" #the city config file is the argument to python script
    python3 ../../scripts/system_metrics.py "$(pwd)/city_config/$cityname"
    python3 ../../scripts/visualisation.py "$(pwd)/city_config/$cityname"
    python3 ../../scripts/legs_dest.py "$(pwd)/city_config/$cityname"
    python3 ../../scripts/report.py "$(pwd)/city_config/$cityname"
    echo "Completed .."
done



