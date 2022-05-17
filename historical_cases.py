import os

import pandas
import requests
from bs4 import BeautifulSoup

from common_utils import BASE_URLS, parse_cases_table, parse_cases_details_table


def scrap_historical_cases():
        response = requests.get(BASE_URLS['HistoricalCases'].format("1"))

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_cases_table(soup)

        data = pandas.DataFrame(res, columns=['Case Number', 'Defendant\'s Name', 'Offence Date', 'Local Authority',
                                             'Main Activity'])

        data['Time-st'] = pandas.to_datetime('today').utcnow()

        try:
            os.makedirs('HistoricalCases')
        except FileExistsError:
            pass

        data.head(10).to_csv('HistoricalCases/historical_cases.csv', index=False)

        i = 2

        while True:

            response = requests.get(BASE_URLS['HistoricalCases'].format(i))
            soup = BeautifulSoup(response.text, 'lxml')

            res = parse_cases_table(soup)
            res.pop()
            if len(res) <= 0:
                print('No more historical cases to show.')
                return

            data = pandas.DataFrame(res,
                                    columns=['Case Number', 'Defendant\'s Name', 'Offence Date', 'Local Authority',
                                             'Main Activity'])
            data['Time-st'] = pandas.to_datetime('today').utcnow()
            data.head(10).to_csv('HistoricalCases/historical_cases.csv', index=False, mode='a', header=False)

            i += 1


def scrap_historical_cases_details():

    df = pandas.read_csv(f'HistoricalCases/historical_cases.csv', sep='\t')

    for i in range(0, len(df)):
        case_number = df.iat[i, 0].split(',')[0]

        response = requests.get(
            'https://resources.hse.gov.uk/convictions-history/case/case_details.asp?SF=CN&SV=' + case_number)

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_cases_details_table(soup)
        res.insert(0, case_number)

        try:
            new_df = pandas.DataFrame(
                [res],
                columns=[
                    'Case Number', 'Defendant', 'Description', 'Offence Date',
                    'Total Fine', 'Total Costs Awarded to HSE', 'Address', 'Region', 'Local Authority', 'Industry',
                    'Main Activity', 'Type of Location', 'HSE Group', 'HSE Directorate', 'HSE Area', 'HSE Division'
                ]
            )
            new_df['Time-st'] = pandas.to_datetime('today').utcnow()
        except ValueError:
            print('Can\'t create new dataframe!')
            continue

        new_df.head(10).to_csv(f'HistoricalCases/{case_number}.csv', index=False)
