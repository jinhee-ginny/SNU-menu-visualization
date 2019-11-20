# load libraries
import requests
import os
import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup
from tqdm import tqdm

original_url = 'http://mini.snu.kr/cafe/set/'
today = datetime.today()
today_str = today.strftime('%Y%m%d')
dates_idx = pd.date_range(start='20060103', end=today_str)

curr_path = os.path.dirname(os.path.abspath('__file__'))
menu_save_path = f'{curr_path}/school_food_{today_str}.csv'

meal_times = {'아침': 'breakfast', '점심': 'lunch', '저녁': 'dinner'}
df = pd.DataFrame(columns=['date', 'meal_time', 'cafeteria', 'menu', 'price', 'etc'])
for date_idx in tqdm(dates_idx):
    date = date_idx.strftime('%Y-%-m-%-d')  # 2019-1-4
    url = original_url + date
    res = requests.get(url)
    res.raise_for_status()
    res.encoding = 'utf-8'

    soup = BeautifulSoup(res.text, 'html.parser')
    menu_table = soup.select('#main > table:nth-of-type(1) > tr')

    for menu_info in menu_table:
        menu_contents = menu_info.contents
        # check meal time
        if menu_contents[0].text in meal_times:
            meal_time = meal_times[menu_contents[0].text]
        else:
            # extract cafeteria/price infomation
            cafeteria = menu_info.find(class_='head bg_menu2').get_text()
            prices = [price.get_text(strip=True) for price in menu_info.find_all(class_='price')]

            # extract menu information
            if prices or (cafeteria == '302동'):
                menu_content = str(menu_contents[-1])
                menus_dirty = menu_content.split('</span>')

                menus = []
                etcs = []
                for menu_dirty in menus_dirty:
                    # TODO: handle exception - halal menu
                    # if '할랄' in menu_dirty:
                    #     etcs.append('halal')
                    if not menu_dirty.startswith('<'):
                        if '🐖' in menu_dirty:
                            etcs.append('no_pork')
                        elif '🥗' in menu_dirty:
                            etcs.append('vegetarian')
                        else:
                            etcs.append('N/A')  # TODO: unite N/A & None value
                        menu = menu_dirty.split('<')[0].strip()

                        # handle exception - 302 cafeteria
                        if cafeteria == '302동':
                            menu_302 = [item for i, item in enumerate(menu.split()) if i % 2 == 0]
                            price_302 = [item for i, item in enumerate(menu.split()) if i % 2 == 1]
                            menus.extend(menu_302)
                            prices.extend(price_302)
                        else:
                            menus.append(menu)

                # append row to dataframe
                for (menu, price, etc) in zip(menus, prices, etcs):
                    df_row = pd.DataFrame([[date, meal_time, cafeteria, menu, price, etc]],
                                          columns=['date', 'meal_time', 'cafeteria', 'menu', 'price', 'etc'])
                    df = df.append(df_row)
            else:
                menus = []
                menus_html = menu_info.find_all(class_='menu')
                # handle exception - menus splitted with /
                for menu_html in menus_html:
                    menu = menu_html.get_text(strip=True).split('/')
                    menus.extend(menu)

                for menu in menus:
                    df_row = pd.DataFrame([[date, meal_time, cafeteria, menu, None, None]],
                                          columns=['date', 'meal_time', 'cafeteria', 'menu', 'price', 'etc'])
                    df = df.append(df_row)

df.to_csv(menu_save_path, index=False)