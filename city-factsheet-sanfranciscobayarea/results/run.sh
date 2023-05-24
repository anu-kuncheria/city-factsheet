set -e  # exit immediately if a command exits with a non-zero status
pwd

#cupertino livermore milpitas palo_alto atherton santa_clara

for cityname in dublin; do
    echo "======= Running ${cityname}======="

    # python3 ../scripts/etl.py "$(pwd)/city_config/$cityname" #the city config file is the argument to python script
    # python3 ../scripts/system_metrics.py "$(pwd)/city_config/$cityname"
    # python3 ../scripts/visualisation.py "$(pwd)/city_config/$cityname"
    # python3 ../scripts/communities_concern.py "$(pwd)/city_config/$cityname"
    # python3 ../scripts/truck.py "$(pwd)/city_config/$cityname" 
    # python3 ../scripts/links_reclassification.py "$(pwd)/city_config/$cityname"
    # python3 ../scripts/triplegs_metrics.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/report.py "$(pwd)/city_config/$cityname"

    echo "Completed .."
done



