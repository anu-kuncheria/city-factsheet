import sys
sys.path.append("general_config")
from load_data import *
from triplegs_metrics import total_trips
from commute_trips import trips_start
from communities_concern import coc_bg

citystat_df = pd.read_csv(citystat_path)
pop = int(citystat_df[citystat_df['city'] == city_name]
          ['population'].values[0])
population = "{:,}".format(int(pop))
area = citystat_df[citystat_df['city'] == city_name]['Area_sqmiles'].values[0]
area = "{:,}".format(int(area))

totaltrips_ending = "{:,}".format(total_trips())
totaltrips_starting = trips_start(trips_start_city_path)
totaltrips_starting = "{:,}".format(totaltrips_starting)


cityStat = """
<html>
<body>
<h1> %s </h1>
<h2> City Statistics </h2>
<p> %s city in California is %s sq. miles and has a population of %s.  </p>
</body>
</html>""" % (city_name_report, city_name_report, area, population)

networkStat = """
<html>
<body>
<h2> Network and Traffic Characteristics </h2>
</body>
</html>"""

systemStat = """
<html>
<body>
<h2> Traffic Metrics </h2>
<p>  Average daily traffic (ADT) (fig 1), Delay (fig 2), and Fuel consumption (fig 3) across links are shown below.
</p>
</body>

</html>"""

adtStat = """
<html>
<body>
<h2> Streets with the highest flow </h2>
<p> The map displays streets with the highest Average Daily Traffic (ADT) categorized by road class.
</p>
</body>
</html>"""

truck = """
<html>
<body>
<h2> Truck Traffic </h2>
<p> The figure below displays the average daily truck traffic on city streets. 
The bar chart illustrates the truck vehicle miles traveled (VMT) categorized by time of day.
</body>
</html>"""

trips = """
<html>
<body>
<h2> Trip Legs Profile </h2>
<p>  The number of trips originating from the city is %s and the number of trips ending in the city is %s. 
The bar graph illustrates the distribution of trips by purpose that end within the city. 
The figure on the right presents a heatmap showcasing the destinations of work trips.
</p>
</body>
</html>""" % (totaltrips_starting, totaltrips_ending)

cocbg = coc_bg()
coc = """
<html>
<body>
<h2> Communities of Concern </h2>
<p> MTC's Communities of Concern in %s comprises of %s Block Groups(BG) with concern flags ranging from high, higher and highest (figure below). Their share of VMT, VHD and Fuel can be seen in the table below. </p>
</body>
</html>""" % (city_name_report, cocbg)

aboutMobiliti = """
<html>
<body>
<h2> About Mobiliti </h2>
<p> Mobiliti is an agent-based scalable parallel discrete event simulation platform. It ingests a road network and a travel demand model to produce a temporal representation of
the traffic dynamics. The routing algorithm for generating the dynamics is a shortest travel time route, and a portion of the trips are given the ability to dynamically re-route when the vehicle starts to experience delays from congestion.</p>

<p> <b> Authored by: </b> Anu Kuncheria and Jane Macfarlane </p>
<p> <b> Contributors: </b> Cy Chan, Colin Laurence, Dimitris Vlachogiannis, Prasanna Balaprakash, Tanwi Mallick </p>

<p> <b> References </b> </p>
<ul>
  <li> Chan, C., Kuncheria, A., & Macfarlane, J. (2023). Simulating the Impact of Dynamic Rerouting on Metropolitan-scale Traffic Systems. ACM Transactions on Modeling and Computer Simulation, 33(1–2), 7:1-7:29. https://doi.org/10.1145/3579842 </li>
  <li> Chan,C., Wang,B., Bachan,J., & Macfarlane,J. (2018). Mobiliti: Scalable Transportation Simulation Using High-Performance Parallel Computing, 21st International Conference on Intelligent Transportation Systems (ITSC), Nov. 2018, pp. 634–641, iSSN: 2153-0017 </li>
  <li> Kuncheria, A., Walker, J.L. and Macfarlane, J. (2023). Socially-aware evaluation framework for transportation, Transportation Letters, pp. 1–18. Available at: https://doi.org/10.1080/19427867.2022.2157366. </li>
  <li> Chan,C., Kuncheria,A., Zhao,B., Cabannes,T., Keimer,A., Wang,B., Bayen,A., & Macfarlane,J. Quasi-Dynamic Traffic Assignment using High Performance Computing, arXiv:2104.12911 [cs], Apr. 2021 </li>
</ul>

</body>
</html>
"""
