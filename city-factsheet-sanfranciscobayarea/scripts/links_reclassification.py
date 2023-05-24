import sys
sys.path.append("general_config")
from load_data import *
import utility as util

logger.info(f" Started script {os.path.basename(__file__)}")
write_directory = os.path.join(processed_path, city_name, 'figures')


def reclassifynetwork_barchart():
    # only relevant attribute is linkid and new_classi fields
    reclassifylinks = gpd.read_file(relinkspath)
    city_links = gpd.read_file(citylinks_path)
    links_re = pd.merge(city_links, reclassifylinks[['LINK_ID', 'new_classi']], left_on='LINK_ID', right_on='LINK_ID',
                        how='left')

    g = {'Residential': ['Neighbourhood Residential street', 'Residential Throughway'],
         'Commercial': ['Neighbourhood Commercial street', 'Commercial Throughway'],
         'Highway': ['Highway'],
         'Rest': ['Industrial street', 'Other/Openspace_street', 'PSP street']}
    g_abr = {'Neighbourhood Residential street': 'NR', 'Residential Throughway': 'RT',
             'Neighbourhood Commercial street': 'NC', 'Commercial Throughway': 'CT',
             'Highway': 'H', 'Industrial street': 'I', 'Other/Openspace_street': 'O', 'PSP street': 'P'}

    newg = {k: oldk for oldk, oldv in g.items() for k in oldv}
    links_re['group'] = links_re['new_classi'].map(newg)
    group_names = ['Residential', 'Commercial', 'Highway', 'Rest']
    # print(links_re.columns)
    group_size = [links_re[links_re['group'] == i]
                  ['LENGTH(meters)'].sum() for i in group_names]
    subgroup_names = []
    [[subgroup_names.append(i) for i in g[k]] for k in g.keys()]
    subgroup_size = [links_re[links_re['new_classi'] == i]
                     ['LENGTH(meters)'].sum() for i in subgroup_names]
    mToMile = 0.000621371
    subgroup_size = [i * mToMile for i in subgroup_size]
    subgroup_abr = [g_abr[i] for i in subgroup_names]

    # lables
    netperc = (subgroup_size / np.sum(subgroup_size) * 100).astype(int)
    lab = []
    [lab.append(str(v) + ':' + str(k)) for k, v in g_abr.items()]
    labels_perc = []
    for i in range(len(lab)):
        labels_perc.append(lab[i] + ' ' + str(netperc[i]) + '%')

    # Barplot
    a, b, c, d = [plt.cm.Blues, plt.cm.Reds, plt.cm.Greys, plt.cm.Greens]
    colors = {'NR': a(0.5), 'RT': a(0.4), 'NC': b(0.5), 'CT': b(
        0.4), 'H': c(0.6), 'I': d(0.5), 'O': d(0.4), 'P': d(0.3)}
    fig, ax = plt.subplots()
    ax.bar(subgroup_abr, subgroup_size,
           label=subgroup_abr, color=colors.values())
    plt.xlabel("Categories")
    plt.ylabel("Network length (miles)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[label])
               for label in colors.keys()]
    plt.legend(handles, labels_perc, loc="best")
    fig.savefig(os.path.join(write_directory,
                f"barplot_reclassify_{city_name}.png"), bbox_inches='tight')


if __name__ == "__main__":
    reclassifynetwork_barchart()
    logger.info(f" === Completed script {os.path.basename(__file__)} ====")
