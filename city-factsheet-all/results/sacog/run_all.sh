
set -e  

directory_path="city_config"
subdirectories=$(find "$directory_path" -mindepth 1 -type d -exec basename {} \;) # lists the subdirectories

for cityname in $subdirectories; do
    echo "======= Running ${cityname}======="
    python3 ../../scripts/etl.py "$(pwd)/city_config/$cityname" #the city config file is the argument to python script
    python3 ../../scripts/system_metrics.py "$(pwd)/city_config/$cityname"
    python3 ../../scripts/visualisation.py "$(pwd)/city_config/$cityname"
    python3 ../../scripts/legs_dest.py "$(pwd)/city_config/$cityname"
    python3 ../../scripts/report.py "$(pwd)/city_config/$cityname"
    echo "Completed .."
done



