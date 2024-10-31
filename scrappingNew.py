import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from concurrent.futures import ThreadPoolExecutor

def criar_df (url):
    print(f"[START] url: {url.split('/')[-1]}" )
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.content, 'html.parser')
    atributos1 = soup.find_all('div', class_=('frame-header'))
    atributos2 = soup.find_all('div', class_=('accordion-item'))
    atributos3 = soup.find_all('div', class_=('pedestrian-protection-table'))
    atributos4 = soup.find_all('div', class_=('specification-table table1'))
    atributos5 = soup.find('div', class_=('stars'))
    disc_columns = { 'column_name':[], 'column_value': [] }

    if len(atributos1) == 0 :
        print(f"[END - EMPTY] url: {url.split('/')[-1]}" )
        return pd.DataFrame()
    else:
        for atributo in atributos4:
            atributos_p = atributo.find_all('p')
            for atributo in atributos_p:
                column_name = atributo.find_all('span')[0].get_text().strip()
                column_value = atributo.find_all('span')[1].get_text().strip()
                if column_name != '' and column_value != '':
                    disc_columns['column_name'].append(column_name)
                    disc_columns['column_value'].append(column_value)

        for atributo in atributos1:
            column_name = atributo.find('div', class_='frame-title').get_text().strip()
            column_value = atributo.find('div', class_='frame-points no-frame-info').get_text().strip().split(' ')[0]
            if column_name != '' and column_value != '':
                disc_columns['column_name'].append(column_name)
                disc_columns['column_value'].append(column_value)

        try:
            for atributo in atributos2:
                column_name = atributo.find('div', class_= 'accordion-item-header')
                column_value = atributo.find('div', class_= 'accordion-item-header')
                column_name = atributo.find('div', class_= 'accordion-item-header').contents[0].get_text().strip()
                column_value = atributo.find('div', class_= 'accordion-item-header').contents[1].get_text().strip().split(' ')[0]
                if column_name != '' and column_value != '':
                    disc_columns['column_name'].append(column_name)
                    disc_columns['column_value'].append(column_value)
        except:
            atributos6 = atributos2[:4]
            for atributo in atributos6:
                column_name = atributo.find('div', class_= 'accordion-item-header')
                column_value = atributo.find('div', class_= 'accordion-item-header')
                column_name = atributo.find('div', class_= 'accordion-item-header').contents[0].get_text().strip()
                column_value = atributo.find('div', class_= 'accordion-item-header').contents[1].get_text().strip().split(' ')[0]
                if column_name != '' and column_value != '':
                    disc_columns['column_name'].append(column_name)
                    disc_columns['column_value'].append(column_value)

        for atributo in atributos3:
            atributos_p = atributo.find_all('p')
            for atributo in atributos_p:
                column_name = atributo.find_all('span')[0].get_text().strip()
                column_value = atributo.find_all('span')[1].get_text().strip().split(' ')[0]
                if column_name != '' and column_value != '':
                    disc_columns['column_name'].append(column_name)
                    disc_columns['column_value'].append(column_value)

        img_text = atributos5.find('img')['data-src']
        stars = re.search(r'gfx/stars(.*?)-',img_text,re.IGNORECASE).group(1).strip()
        disc_columns['column_name'].append('rating')
        disc_columns['column_value'].append(stars)

    df = pd.DataFrame(disc_columns)
    df = df.transpose()
    df.reset_index(inplace=True,drop=True)
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.reset_index(drop=True)
    print(f"[END - FULL] url: {url.split('/')[-1]}" )
    return df

def linktodf(urls):
    print('COMEÇOU')
    all_vehicles_data = pd.DataFrame()
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(criar_df, urls)
        for vehicle_df in results:
            if not vehicle_df.empty:
                if all_vehicles_data.empty:
                    all_vehicles_data = vehicle_df.copy()
                else:
                    for df in [all_vehicles_data, vehicle_df]:
                      df.columns = pd.io.common.dedup_names(df.columns, is_potential_multiindex=False)
                    all_vehicles_data = pd.concat([all_vehicles_data, vehicle_df], axis=0)
                all_vehicles_data.to_csv(r'C:\Users\jonat\Desktop\Dados\EURO_NCAP\scrappingNewDf.csv', index=False, encoding='utf-8', sep=',')
    print('TERMINOU')

urlStart = 'https://www.euroncap.com/en/results/suzuki/ignis/'
urls = [urlStart + str(i) for i in range(5000,55000)]
# urls = [urlStart + str(i) for i in range(49700,50000)]
linktodf(urls)