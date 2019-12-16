import requests
import geopy.distance
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

mpl.rcParams['font.family'] = 'Gulim'

GEOCODE_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
DIRECTIONS_API_URL = 'https://maps.googleapis.com/maps/api/directions/json'
API_KEY = 'AIzaSyAnmA7OpmbRdkOK-Ala2S-IRsQYTWLiIQM'

addresses = ['서울특별시 신림동 서울대학교 학생회관',
             '서울특별시 신림동 서울대학교 제3식당',
             '서울특별시 봉천동 서울대학교 기숙사신관',
             '서울특별시 신림동 서울대학교 제2공학관',
             '서울특별시 신림동 서울대학교 동원생활관',
             '서울특별시 신림동 서울대학교 자하연식당']

abb = ['학생회관', '전망대(농대)', '기숙사(919동)', '302동', '동원관', '자하연']

gps = dict()

for address in addresses:
    params = {
        'address': address,
        'sensor': 'false',
        'region': 'South Korea',
        'key': API_KEY
    }

    req = requests.get(GEOCODE_API_URL, params=params)
    res = req.json()

    result = res['results'][0]

    gps[address] = {'lat': result['geometry']['location']['lat'],
                    'lng': result['geometry']['location']['lng']}


def get_dist(origin, destination):
    coords_1 = (origin['lat'], origin['lng'])
    coords_2 = (destination['lat'], destination['lng'])
    return geopy.distance.geodesic(coords_1, coords_2).km


rows = []
for address_i in addresses:
    row = []
    for address_j in addresses:
        row.append(get_dist(gps[address_i], gps[address_j]))
    rows.append(pd.Series(row))
dist_df = pd.DataFrame(rows, index=abb)
dist_df.columns = abb

dist_df.to_csv('distance.csv', encoding='euc-kr')


def subset_list(L):
    for i in range(len(L)):
        j = i + 1
        while j < len(L):
            yield (L[i], L[j])
            j += 1


pairs = list(subset_list(abb))

weights = []
for pair in pairs:
    weights.append(1/(dist_df.loc[pair[0]][pair[1]])**2)

G = nx.Graph()
G.add_nodes_from(abb)
for pair in pairs:
    G.add_edges_from([pair], weight=1/(dist_df.loc[pair[0]][pair[1]])**2)
elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 1.33]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 1.33]
pos = nx.spring_layout(G, weight='weight')
nx.draw_networkx_nodes(G, pos, node_size=700)
nx.draw_networkx_edges(G, pos, edgelist=elarge,
                       width=2)
nx.draw_networkx_edges(G, pos, edgelist=esmall,
                       width=2, alpha=0.5, edge_color='b', style='dashed')
nx.draw_networkx_labels(G, pos, font_size=10, font_family='Gulim')
plt.axis('off')
plt.show()

df = pd.read_csv('dist_df.csv', encoding='euc-kr', header=None)
df[2] = weights
df.to_csv('dist_df_2.csv', header=False, encoding='euc-kr', index=False)

np.corrcoef(df[1], df[2])
