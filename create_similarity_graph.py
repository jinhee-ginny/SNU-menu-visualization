import re
from tqdm import tqdm

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import networkx as nx

csv_path = 'C:/Users/toooo/Documents/GitHub/SNU-menu-visualization/file/school_food_20191215.csv'
target_cafe = ['학생회관', '전망대(농대)', '기숙사(919동)', '302동', '동원관', '자하연']

def filter_menu(menu_str):
    menu_str = re.sub('[^ ㄱ-ㅣ가-힣]+', '', menu_str).replace('\n', '').replace('🥗', '')
    nontarget_words = ['휴관', '휴점', '연휴', '휴일', '휴무', '설날', '신정', '추석', '기념일', '중단', '🥗']
    if menu_str and not any(menu in menu_str for menu in nontarget_words):
        return menu_str
def levenshtein_distance(s1, s2, debug=False):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1, debug)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))

        if debug:
            print(current_row[1:])

        previous_row = current_row

    return previous_row[-1]


df = pd.read_csv(csv_path)
# drop weird in menu_string
df = df.dropna(subset=['menu'])
df['menu'] = df['menu'].apply(filter_menu)
df = df.dropna(subset=['menu'])

# Analysis per cafeteria
df_a = df[df.cafeteria == '학생회관'].drop('cafeteria', axis=1)
df_b = df[df.cafeteria == '전망대(농대)'].drop('cafeteria', axis=1)
df_c = df[df.cafeteria == '기숙사(919동)'].drop('cafeteria', axis=1)
df_e = df[df.cafeteria == '302동'].drop('cafeteria', axis=1)
df_f = df[df.cafeteria == '동원관'].drop('cafeteria', axis=1)
df_g = df[df.cafeteria == '자하연'].drop('cafeteria', axis=1)

# match the dates(starting froms)
df_menu_a = df_a.set_index(['date', 'meal_time'])['menu']
df_menu_b = df_b.set_index(['date', 'meal_time'])['menu']
df_menu_c = df_c.set_index(['date', 'meal_time'])['menu']
df_menu_e = df_e.set_index(['date', 'meal_time'])['menu']
df_menu_f = df_f.set_index(['date', 'meal_time'])['menu']
df_menu_g = df_g.set_index(['date', 'meal_time'])['menu']

# calculate levenshtein_distance between two cafateria menu

df_menus = [df_menu_a, df_menu_b, df_menu_c, df_menu_e, df_menu_f, df_menu_g]


def subset_list(L):
    for i in range(len(L)):
        j = i + 1
        while j < len(L):
            yield (L[i], L[j])
            j += 1


distances = {}
cafeteria_pairs = list(subset_list(target_cafe))
for i, (menus_1, menus_2) in enumerate(subset_list(df_menus)):
    menu_pair = pd.merge(menus_1, menus_2, how='outer', on=['date', 'meal_time'])
    menu_pair.dropna(inplace=True)
    menu_pair.sort_index(inplace=True)
    dist_list = []
    for date in tqdm(np.unique([date for (date, _) in menu_pair.index])):
        distance = menu_pair.loc[date].apply(lambda row: levenshtein_distance(row['menu_x'], row['menu_y']), axis=1)
        distance_mean = distance.groupby('meal_time').agg(np.mean)
        df_temp = pd.DataFrame([distance_mean], index=[date])
        dist_list.append(df_temp)
    distances[cafeteria_pairs[i]] = pd.concat(dist_list, copy=False, sort=False)

mean_distances = []
for pair in cafeteria_pairs:
    print(pair)
    mean = 1 / distances[pair].mean().mean()
    print(mean)
    mean_distances.append(mean)

# make graph
# create node and edges
G = nx.Graph()
G.add_nodes_from(target_cafe)
for pair in cafeteria_pairs:
    G.add_edges_from([pair], weight=1 / distances[pair].mean().mean())

elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 0.14]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.14]

# %%
pos = nx.spring_layout(G, weight='weight')
# draw nodes
nx.draw_networkx_nodes(G, pos, node_size=700)

# draw edges
nx.draw_networkx_edges(G, pos, edgelist=elarge,
                       width=2)
nx.draw_networkx_edges(G, pos, edgelist=esmall,
                       width=2, alpha=0.5, edge_color='b', style='dashed')

# draw labels
nx.draw_networkx_labels(G, pos, font_size=10, font_family='AppleGothic')
plt.axis('off')
plt.show()
# %%

dist = []
index = []
for pair in cafeteria_pairs:
    dist.append(1 / distances[pair].mean().mean())
    index.append(f'{pair[0]} ~ {pair[1]}')
df = pd.DataFrame(dist, index=index)
df.to_csv('dist_df.csv', header=False, encoding='euc-kr')
