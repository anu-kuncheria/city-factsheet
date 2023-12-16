set -e  

for cityname in napa palo_alto cupertino dublin fremont santa_clara; do
    echo "======== Running ${cityname} ========"

    python3 ../scripts/etl.py "$(pwd)/city_config/$cityname" #the city config file is the argument to python script
    python3 ../scripts/system_metrics.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/visualisation.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/communities_concern.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/truck.py "$(pwd)/city_config/$cityname" 
    python3 ../scripts/links_reclassification.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/triplegs_metrics.py "$(pwd)/city_config/$cityname"
    python3 ../scripts/report.py "$(pwd)/city_config/$cityname"
    echo ".. Completed .."
done



