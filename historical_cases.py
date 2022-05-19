import os
import time
import urllib.error

import pandas
import requests
from bs4 import BeautifulSoup

from common_utils import BASE_URLS, parse_cases_breaches_table, parse_cases_details_table


def scrape_historical_cases():
    response = requests.get(BASE_URLS['HistoricalCases'].format("1"))

    soup = BeautifulSoup(response.text, 'lxml')
    res = parse_cases_breaches_table(soup)
    res.pop()

    data = pandas.DataFrame(res, columns=['case_number', 'defendant\'s_name', 'offence_date', 'local_authority',
                                          'main_activity'])

    data['cytora_ingest_ts'] = time.time()

    try:
        os.makedirs('HistoricalCases')
    except FileExistsError:
        pass

    data.to_csv('HistoricalCases/historical_cases.csv', index=False)

    i = 2
    while True:
        try:
            response = requests.get(BASE_URLS['HistoricalCases'].format(i))
            soup = BeautifulSoup(response.text, 'lxml')

            res = parse_cases_breaches_table(soup)
            res.pop()

            if len(res) <= 0:
                print('No more historical cases to show.')
                return

            data = pandas.DataFrame(res,
                                    columns=['case_number', 'defendant\'s_name', 'offence_date', 'local_authority',
                                             'main_activity'])
            data['cytora_ingest_ts'] = time.time()
            data.head(10).to_csv('HistoricalCases/historical_cases.csv', index=False, mode='a', header=False)

            i += 1
        except urllib.error.HTTPError:
            print('Bad request')
            print(f'At index: {i}')
            print(f'At URL: {BASE_URLS["HistoricalCases"].format(i)}')
            return


def scrape_historical_cases_details(cases: list = None):
    errors = set()
    errors_arr = []
    success = set()
    success_arr = []

    if cases:
        for i in range(0, len(cases)):
            case_number = cases[i].get('case_id')

            a = fetch_historical_cases_details(case_number)

            if not a.get('state'):
                errors.add(a.get('case_id'))
                errors_arr.append(a)
            else:
                success.add(a.get('case_id'))
                success_arr.append(a)
    else:
        with open('HistoricalCases/historical_cases.csv', 'r') as file:

            for row in file:
                record = row.split(',')

                if 'case_number' in record:
                    continue
                case_number = record[0]

                a = fetch_historical_cases_details(case_number)

                if not a.get('state'):
                    errors.add(a.get('case_id'))
                    errors_arr.append(a)
                else:
                    success.add(a.get('case_id'))
                    success_arr.append(a)

    print('Errors: ' + str(errors))
    print('Successful: ' + str(success))
    print(len(success_arr))


def fetch_historical_cases_details(case_id: str) -> dict:
    try:
        response = requests.get(
            'https://resources.hse.gov.uk/convictions-history/case/case_details.asp?SF=CN&SV=' + case_id)

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_cases_details_table(soup)
        res.insert(0, case_id)

        new_df = pandas.DataFrame(
            [res],
            columns=[
                'case_number', 'defendant', 'description', 'offence_date',
                'total_fine', 'total_costs_awarded_to_hse', 'address', 'region', 'local_authority', 'industry',
                'main_activity', 'type_of_location', 'hse_group', 'hse_directorate', 'hse_area', 'hse_division'
            ]
        )

        new_df['cytora_ingest_ts'] = time.time()

        file_path = f'HistoricalCases/{case_id}.csv'
        new_df.to_csv(file_path, index=False)

        return {
            'state': True,
            'file_path': file_path,
            'case_id': case_id,
        }
    except ValueError as e:
        return {
            'state': False,
            'error': str(e),
            'case_id': case_id,
        }
