import os
import pandas
import requests
from bs4 import BeautifulSoup
from common_utils import BASE_URLS, NOTICES_KEYS, ENDPOINTS, parse_details_table
from sourse import NOTICES


def scrap_notices():
    for dict in NOTICES:

        for key, value in dict.items():
            df = pandas.read_html(BASE_URLS['Notices'].format("1") + NOTICES_KEYS[key] + ENDPOINTS['Notices'], header=0)
            df[0]['Time-st'] = pandas.to_datetime('today').utcnow()

            data = df[0][
                ['Notice Number', 'Recipient\'s Name', 'Notice Type', 'Issue Date', 'Local Authority', 'Main Activity',
                 'Time-st']]

            try:
                os.makedirs('Notices/' + key)
            except FileExistsError:
                pass

            data.head(10).to_csv(f'Notices/{key}/{key}.csv', index=False)

            # response = requests.get(BASE_URLS['Notices'].format("1") + NOTICES_KEYS[key] + ENDPOINTS['Notices'])
            # soup = BeautifulSoup(response.text, 'lxml')
            # In production, I will use get_pages_number(soup) function, but I have hard coded it for development goals

            for i in range(2, 30):
                df = pandas.read_html(BASE_URLS['Notices'].format(i) + NOTICES_KEYS[key] + ENDPOINTS['Notices'], header=0)
                df[0]['Time-st'] = pandas.to_datetime('today').utcnow()

                data = df[0]
                data.head(10).to_csv(f'Notices/{key}/{key}.csv', index=False, mode='a', header=False)


def scrap_notices_details():
    for key in NOTICES_KEYS.keys():

        df = pandas.read_csv(f'Notices/{key}/{key}.csv', sep='\t')

        for i in range(0, len(df)):
            param = df.iat[i, 0].split(',')[0]
            response = requests.get('https://resources.hse.gov.uk/notices/notices/notice_details.asp?SF=CN&SV=' + param)

            soup = BeautifulSoup(response.text, 'lxml')
            res = parse_details_table(soup)

            new_df = pandas.DataFrame(
                [res],
                columns=[
                    'Notice Type', 'Description', 'Compliance Date',
                    'Revised Compliance Date', 'Result'
                ]
            )
            new_df['Time-st'] = pandas.to_datetime('today').utcnow()

            try:
                os.makedirs(f'Notices/{key}')
            except FileExistsError:
                pass

            new_df.head(10).to_csv(f'Notices/{key}/' + param + '.csv', index=False)
