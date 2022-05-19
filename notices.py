import os
import time
import urllib.error

import pandas
import requests
from bs4 import BeautifulSoup
from common_utils import BASE_URLS, parse_notices_details_table


def scrape_notices():
    df = pandas.read_html(BASE_URLS['Notices'].format("1"), header=0)
    df[0].drop(df[0].tail(1).index, inplace=True)
    df[0]['cytora_ingest_ts'] = time.time()

    data = df[0][
        ['Notice Number', 'Recipient\'s Name', 'Notice Type', 'Issue Date', 'Local Authority', 'Main Activity',
         'cytora_ingest_ts']]

    data.columns = ['_'.join(col.lower().split(' ')) for col in data.columns]

    # change it to with statement
    try:
        os.makedirs('Notices')
    except FileExistsError:
        pass

    data.to_csv(f'Notices/notices.csv', index=False)

    # In production, I will use get_pages_number(soup) function, but I have hard coded it for development goals

    # i = 2
    # while True:
    #     df = pandas.read_html(BASE_URLS['Notices'].format(i), header=0)
    #     df[0]['Time-st'] = pandas.to_datetime('today').utcnow()
    #     df[0].drop(df[0].tail(1).index, inplace=True)
    #
    #     data = df[0]
    #     data.head(10).to_csv(f'Notices/notices.csv', index=False, mode='a', header=False)
    #     i += 1

    for i in range(2, 3):
        try:
            df = pandas.read_html(BASE_URLS['Notices'].format(i), header=0)
            df[0]['cytora_ingest_ts'] = time.time()
            df[0].drop(df[0].tail(1).index, inplace=True)

            df[0].to_csv(f'Notices/notices.csv', index=False, mode='a', header=False)
        except urllib.error.HTTPError:
            print('Bad request')
            print(f'At index: {i}')
            print(f'At URL: {BASE_URLS["Notices"].format(i)}')
            return


def scrape_notices_details(notices: list = None):
    errors = set()
    errors_arr = []
    success = set()
    success_arr = []

    if notices:
        for i in range(0, len(notices)):

            notice_number = notices[i].get('notice_id')
            served_date = notices[i].get('served_date')
            recipient_name = notices[i].get('recipient_name')

            a = fetch_notices_details(notice_number, recipient_name, served_date)

            if not a.get('state'):
                errors.add(a.get('notice_id'))
                errors_arr.append(a)
            else:
                success.add(a.get('notice_id'))
                success_arr.append(a)
    else:
        with open('Notices/notices.csv', 'r') as file:

            for row in file:
                record = row.split(',')
                if 'notice_number' in record:
                    continue
                notice_number = record[0]
                served_date = record[3]
                recipient_name = record[1]

                a = fetch_notices_details(notice_number, recipient_name, served_date)

                if not a.get('state'):
                    errors.add(a.get('notice_id'))
                    errors_arr.append(a)
                else:
                    success.add(a.get('notice_id'))
                    success_arr.append(a)

    print('Errors: ' + str(errors))
    print('Successful: ' + str(success))
    print(len(success_arr))


def fetch_notices_details(notice_id: str, recipient_name: str, served_date: str) -> dict:
    try:
        response = requests.get(
            'https://resources.hse.gov.uk/notices/notices/notice_details.asp?SF=CN&SV=' + notice_id)
        soup = BeautifulSoup(response.text, 'lxml')
        res, col = parse_notices_details_table(soup)

        columns = ['_'.join(c.lower().split()) for c in col]

        res.insert(0, served_date)
        res.insert(0, recipient_name)
        res.insert(0, notice_id)

        new_df = pandas.DataFrame(
            [res],
            columns=[
                        'notice_number', 'recipient_name', 'served_date',
                    ] + columns
        )

        new_df['cytora_ingest_ts'] = time.time()

        file_path = f'Notices/{notice_id}.csv'
        new_df.to_csv(file_path, index=False)

        return {
            'state': True,
            'file_path': file_path,
            'notice_id': notice_id,
        }
    except ValueError as e:
        return {
            'state': False,
            'error': str(e),
            'notice_id': notice_id,
            'served_date': served_date,
            'recipient_name': recipient_name
        }
