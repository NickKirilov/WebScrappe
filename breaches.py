import os

import pandas
import requests
from bs4 import BeautifulSoup

from common_utils import BASE_URLS, parse_cases_table, get_pages_number, parse_cases_details_table, \
    parse_breaches_details_table


def scrap_breaches():
        response = requests.get(BASE_URLS['Breaches'].format("1"))

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_cases_table(soup)

        data = pandas.DataFrame(res, columns=['Case/Breach', 'Defendant\'s Name', 'Hearing Date', 'Result',
                                              'Fine £', 'Act or Regulation'])

        data['Time-st'] = pandas.to_datetime('today').utcnow()

        try:
            os.makedirs('Breaches')
        except FileExistsError:
            pass

        data.head(10).to_csv('Breaches/breaches.csv', index=False)

        pages = get_pages_number(soup)

        for i in range(2, pages+1):

            response = requests.get(BASE_URLS['Breaches'].format(i))
            soup = BeautifulSoup(response.text, 'lxml')

            res = parse_cases_table(soup)
            res.pop()

            data = pandas.DataFrame(res,
                                    columns=['Case/Breach', 'Defendant\'s Name', 'Hearing Date', 'Result',
                                             'Fine £', 'Act or Regulation'])
            data['Time-st'] = pandas.to_datetime('today').utcnow()
            data.head(10).to_csv('Breaches/breaches.csv', index=False, mode='a', header=False)


def scrap_breaches_details():

    df = pandas.read_csv(f'Breaches/breaches.csv', sep='\t')

    for i in range(0, len(df)):
        case_number, breach_number = df.iat[i, 0].split(',')[0].split('/')

        endpoint = case_number + breach_number
        response = requests.get('https://resources.hse.gov.uk/convictions/breach/breach_details.asp?SF=BID&SV=' + endpoint)

        case_number = case_number[:-1]

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_breaches_details_table(soup)
        res.insert(0, breach_number)
        res.insert(0, case_number)

        try:
            new_df = pandas.DataFrame(
                [res],
                columns=[
                    'Case Number', 'Breach Number', 'Defendant', 'Court Name', 'Court Level', 'Act', 'Regulation',
                    'Date of Hearing', 'Result', 'Fine', 'Address', 'Region',
                    'Local Authority', 'Industry', 'Main Activity', 'Type of Location', 'HSE Group',
                    'HSE Directorate', 'HSE Area', 'HSE Division'
                ]
            )
            new_df['Time-st'] = pandas.to_datetime('today').utcnow()
        except ValueError:
            print('Can\'t create new dataframe!')
            continue

        new_df.head(10).to_csv(f'Breaches/{endpoint}.csv', index=False)
