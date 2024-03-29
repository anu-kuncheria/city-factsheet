
set -e  # exit immediately if a command exits with a non-zero status
pwd

directory_path="city_config"
subdirectories=$(find "$directory_path" -mindepth 1 -type d -exec basename {} \;) # lists the subdirectories

for cityname in $subdirectories; do
    echo "======= Running ${cityname}======="
    python3 ../scripts/etl.py "$(pwd)/city_config/$cityname" 
    python3 ../scripts/system_metrics.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/visualisation.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/communities_concern.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/truck.py "$(pwd)/city_config/$cityname" 
    python3 ../scripts/links_reclassification.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/triplegs_metrics.py "$(pwd)/city_config/$cityname"
    if python3 ../scripts/report.py "$(pwd)/city_config/$cityname"; then
        echo "report.py executed successfully."
    else
        echo "report.py failed. Running Report version2 for non Coc cities"
        python3 ../scripts/report_nococ_cities.py "$(pwd)/city_config/$cityname"
    fi    
    echo ".. Completed .."
done



