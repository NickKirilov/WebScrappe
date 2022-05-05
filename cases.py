import os

import pandas
import requests
from bs4 import BeautifulSoup

from common_utils import BASE_URLS, CASES_KEYS, ENDPOINTS, parse_cases_table, get_pages_number, parse_details_table
from sourse import CASES


def scrap_cases():
    for dict in CASES:

        for key, value in dict.items():
            response = requests.get(BASE_URLS['Cases'].format("1") + CASES_KEYS[key] + ENDPOINTS['Cases'])

            soup = BeautifulSoup(response.text, 'lxml')
            res = parse_cases_table(soup)

            data = pandas.DataFrame(res, columns=['Case Number', 'Defendant\'s Name', 'Offence Date', 'Local Authority',
                                                  'Main Activity'])

            data['Time-st'] = pandas.to_datetime('today').utcnow()

            try:
                os.makedirs('Cases/' + key)
            except FileExistsError:
                pass

            data.head(10).to_csv(f'Cases/{key}/{key}.csv', index=False)

            for i in range(2, get_pages_number(soup) + 1):

                response = requests.get(BASE_URLS['Cases'].format(i) + CASES_KEYS[key] + ENDPOINTS['Cases'])
                soup = BeautifulSoup(response.text, 'lxml')

                res = parse_cases_table(soup)

                data = pandas.DataFrame(res,
                                        columns=['Case Number', 'Defendant\'s Name', 'Offence Date', 'Local Authority',
                                                 'Main Activity'])
                data['Time-st'] = pandas.to_datetime('today').utcnow()

                data.head(10).to_csv(f'Cases/{key}/{key}.csv', index=False, mode='a', header=False)


def scrap_cases_details():
    for key in CASES_KEYS.keys():

        df = pandas.read_csv(f'Cases/{key}/{key}.csv', sep='\t')

        for i in range(0, len(df)):
            param = df.iat[i, 0].split(',')[0]
            response = requests.get('https://resources.hse.gov.uk/convictions/case/case_details.asp?SF=CN&SV=' + param)

            soup = BeautifulSoup(response.text, 'lxml')
            res = parse_details_table(soup)

            try:
                new_df = pandas.DataFrame(
                    [res],
                    columns=[
                        'Defendant', 'Description', 'Offence Date',
                        'Total Fine', 'Total Costs Awarded to HSE'
                    ]
                )
                new_df['Time-st'] = pandas.to_datetime('today').utcnow()
            except ValueError:
                print('Can\'t create new dataframe!')
                continue

            try:
                os.makedirs(f'Cases/{key}')
            except FileExistsError:
                pass

            new_df.head(10).to_csv(f'Cases/{key}/' + param + '.csv', index=False)