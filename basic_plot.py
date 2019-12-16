from collections import Counter
import re

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

csv_path = '/Users/ginny/Documents/GitHub/SNU-menu-visualization/school_food_20191215.csv'
target_cafe = ['학생회관', '전망대(농대)', '기숙사(919동)', '기숙사(901동)', '302동', '동원관', '자하연']

def filter_menu(menu_str):
    menu_str = re.sub('[^ ㄱ-ㅣ가-힣]+', '', menu_str).replace('\n', '').replace('🥗', '')
    nontarget_words = ['휴관', '휴점', '연휴', '휴일', '휴무', '설날', '신정', '추석', '기념일', '중단', '🥗']
    if menu_str and not any(menu in menu_str for menu in nontarget_words):
        return menu_str
def split_menu(menu_str, length):
    letters = [menu_str[i: i + length] for i in range(len(menu_str) - length)]
    length = str(length)
    for letter in letters:
        counters[length][letter] = counters[length].get(letter, 0) + 1

df = pd.read_csv(csv_path)
# drop weird in menu_string
df = df.dropna(subset=['menu'])
df['menu'] = df['menu'].apply(filter_menu)
df = df.dropna(subset=['menu'])

# leave only 직영식당
is_target = df['cafeteria'].apply(lambda x: x in target_cafe)
df = df[is_target]
# df.sample(50)

# Analysis with total_df
count1, count2, count3, count4, count5 = Counter(), Counter(), Counter(), Counter(), Counter()
counters = {'1': count1, '2': count2, '3': count3, '4': count4, '5': count5}
for i in range(1, 6):
    df['menu'].apply(lambda x: split_menu(x, i))

# 1) Frequency
frequency_1 = count1.most_common(20)
frequency_2 = count2.most_common(10)
frequency_3 = count3.most_common(10)
frequency_4 = count4.most_common(10)
frequency_5 = count5.most_common(10)
# %%
sns.set(style='whitegrid')
plt.rcParams['font.family'] = 'AppleGothic'
fig, [(ax1, ax2), (ax3, ax4)] = plt.subplots(2, 2, sharey=True, figsize=(25, 15))
fig.suptitle('Menu Frequency', size=30)
ax1.plot(*zip(*frequency_2), label='two', color='C0', alpha=0.7)
ax2.plot(*zip(*frequency_3), label='three', color='C1', alpha=0.7)
ax3.plot(*zip(*frequency_4), label='four', color='C4', alpha=0.7)
ax4.plot(*zip(*frequency_5), label='five', color='C5', alpha=0.7)
ax1.set_ylim((0, 8500))
ax1.set_ylabel('Letter Counts', size=15)
ax3.set_ylabel('Letter Counts', size=15)
ax1.set_title('Two Letters', color='C0', size=15)
ax2.set_title('Three Letters', color='C1', size=15)
ax3.set_title('Four Letters', color='C4', size=15)
ax4.set_title('Five Letters', color='C5', size=15)
plt.savefig("Menu Frequency.png", bbox_inches='tight')
# %%

# 2) Price
df_price = df[df.price != '??'][df.price != '0'].dropna(subset=['price'])
df_price['price'] = df_price['price'].apply(lambda x: x if re.findall('[0-9]', x) else 'drop')
df_price = df_price[df_price.price != 'drop']
df_price['price'] = pd.to_numeric(df_price['price'])

np.average(df_price['price'])

df_price['year'] = df_price['date'].apply(lambda x: x[:4])
price_info = df_price.groupby('year').describe()['price']

price_info.loc[[str(i) for i in range(2008, 2019)], 'count'].plot(title='연간 SNU 식당 총 제공 메뉴 수')

# %%
fig, ax = plt.subplots(figsize=(10, 7))
ax.errorbar(price_info.index, price_info['mean'] * 100, yerr=price_info['std'] * 100, label='mean', color='C0', alpha=0.5)
ax.plot(price_info.index, price_info['min'] * 100, label='min', color='C1', alpha=0.5)
ax.errorbar(price_info.index, price_info['max'] * 100, label='max', color='C4', alpha=0.5)
ax.set_xlabel('Year', size=15)
ax.set_ylabel('Price(won)', size=15)
ax.set_title('Change of SNU meal price', size=25)
ax.legend()
plt.savefig('Change of SNU meal price.png', bbox_inches='tight')
# %%
