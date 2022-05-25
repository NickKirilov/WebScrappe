import os
import urllib.error
from os.path import exists

import pandas
import requests
from bs4 import BeautifulSoup

from common_utils import BASE_URLS, parse_breaches_details_table, parse_cases_breaches_table


def scrape_historical_breaches():
        response = requests.get(BASE_URLS['HistoricalBreaches'].format("1"))

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_cases_breaches_table(soup)
        res.pop()

        data = pandas.DataFrame(res, columns=['case/breach', 'defendant\'s_name', 'hearing_date', 'result',
                                          'fine £', 'act_or_regulation'])

        data['cytora_ingest_ts'] = pandas.to_datetime('today')
        data['page_id'] = '1'
        try:
            os.makedirs('HistoricalBreaches')
        except FileExistsError:
            pass

        data.to_csv('HistoricalBreaches/historical_breaches.csv', index=False)

        i = 2

        while True:
            try:
                response = requests.get(BASE_URLS['HistoricalBreaches'].format(i))
                soup = BeautifulSoup(response.text, 'lxml')

                res = parse_cases_breaches_table(soup)
                res.pop()
                if len(res) <= 0:
                    print('No more historical breaches to show.')
                    return

                data = pandas.DataFrame(res,
                                        columns=['case/breach', 'defendant\'s_name', 'hearing_date', 'result',
                                                 'fine £', 'act_or_regulation'])
                data['cytora_ingest_ts'] = pandas.to_datetime('today')
                data['page_id'] = str(i)
                data.to_csv('HistoricalBreaches/historical_breaches.csv', index=False, mode='a', header=False)

                i += 1
            except urllib.error.HTTPError:
                print('Bad request')
                print(f'At index: {i}')
                print(f'At URL: {BASE_URLS["HistoricalBreaches"].format(i)}')
                return


def scrape_historical_breaches_details(breaches: list = None):
    errors = set()
    errors_arr = []
    success = set()
    success_arr = []

    cytora_file_ingest_st = pandas.to_datetime('today')

    if breaches:
        for i in range(0, len(breaches)):
            case_number = breaches[i].get('case_id')
            breach_number = breaches[i].get('breach_number')
            endpoint = breaches[i].get('endpoint')

            a = fetch_historical_breaches_details(case_number, breach_number, endpoint, cytora_file_ingest_st)

            if not a.get('state'):
                errors.add(a.get('case_id'))
                errors_arr.append(a)
            else:
                success.add(a.get('case_id'))
                success_arr.append(a)
    else:

        with open('HistoricalBreaches/historical_breaches.csv', 'r') as file:
            for row in file:
                record = row.split(',')
                if 'case/breach' in record:
                    continue

                case_number, breach_number = record[0].split('/')
                endpoint = case_number + breach_number
                case_number = case_number[:-1]
                a = fetch_historical_breaches_details(case_number, breach_number, endpoint, cytora_file_ingest_st)

                if not a.get('state'):
                    errors.add(a.get('case_id'))
                    errors_arr.append(a)
                else:
                    success.add(a.get('case_id'))
                    success_arr.append(a)

    print('Errors: ' + str(errors))
    print('Successful: ' + str(success))
    print(len(success_arr))


def fetch_historical_breaches_details(case_id: str, breach_number: str, endpoint: str, cytora_ingest_time) -> dict:
    try:
        response = requests.get(
            'https://resources.hse.gov.uk/convictions-history/breach/breach_details.asp?SF=BID&SV=' + endpoint)

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_breaches_details_table(soup)
        res.insert(0, breach_number)
        res.insert(0, case_id)
        res.append(endpoint)

        new_df = pandas.DataFrame(
            [res],
            columns=[
                'case_number', 'breach_number', 'defendant', 'court_name', 'court_level', 'act', 'regulation',
                'date_of_hearing', 'result', 'fine', 'address', 'region',
                'local_authority', 'industry', 'main_activity', 'type_of_location', 'hse_group',
                'hse_directorate', 'hse_area', 'hse_division', 'combined_id'
            ]
        )

        new_df['cytora_ingest_ts'] = pandas.to_datetime('today')

        file_path = f'HistoricalBreaches/historical_breaches_details_{cytora_ingest_time}.csv'

        if not exists(file_path):
            new_df.to_csv(file_path, index=False)
        else:
            new_df.to_csv(file_path, index=False, mode='a', header=False)

        return {
            'state': True,
            'file_path': file_path,
            'breach_number': breach_number,
            'case_id': case_id,
            'endpoint': endpoint,
        }
    except ValueError as e:
        return {
            'state': False,
            'error': str(e),
            'breach_number': breach_number,
            'case_id': case_id,
            'endpoint': endpoint,
        }