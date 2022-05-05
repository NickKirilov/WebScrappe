import os
import re
from bs4 import BeautifulSoup
import requests
from sourse import NOTICES, CASES
import pandas

NOTICES_KEYS = {
    'England': '8',
    'Scottland': '9',
    'Wales': '10'
}

CASES_KEYS = {
    'ESE': '2',
    'London': '6',
    'Midlands': '5',
    'NW': '3',
    'Scotland': '7',
    'WalesSW': '1',
    'YorkNE': '4',
}

ENDPOINTS = {
    'Notices': '&EO=%3D&SF=CTR&ST=N&SO=DNIS',
    'Cases': '&SO=ADN'
}

BASE_URLS = {
    'Notices': 'https://resources.hse.gov.uk/notices/notices/notice_list.asp?PN={}&rdoNType=&NT=&SN=P&SV=',
    'Cases': 'https://resources.hse.gov.uk/convictions/case/case_list.asp?PN={}&ST=C&EO=%3D&SN=P&SF=UKR&SV='
}


def get_pages_number(soup):
    total_items = soup.find_all('p')
    matches = re.findall(r'of\s[0-9]+', total_items[2].text)
    if not len(matches):
        total_items = soup.find_all('th', attrs={'colspan': "5"})
        matches = re.findall(r'of\s[0-9]+', total_items[0].text)

    number = int(matches[0][3:])
    return number


def parse_table(soup):
    table = soup.find_all('tr')
    res = []
    for tr in table:
        td = tr.find_all('td')
        row = [tr.text.strip() for tr in td if tr.text.strip()]
        if row:
            res.append(row)

    return res


for dict in NOTICES:

    for key, value in dict.items():
        response = requests.get(BASE_URLS['Notices'].format("1") + NOTICES_KEYS[key] + ENDPOINTS['Notices'])

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

        soup = BeautifulSoup(response.text, 'lxml')

        # In production, I will use "get_pages_number()" function, but I have hard coded it for development goals
        for i in range(2, 30):
            df = pandas.read_html(BASE_URLS['Notices'].format(i) + NOTICES_KEYS[key] + ENDPOINTS['Notices'],
                                  header=0)
            df[0]['Time-st'] = pandas.to_datetime('today').utcnow()

            data = df[0]

            data.head(10).to_csv(f'Notices/{key}/{key}.csv', index=False, mode='a', header=False)


for dict in CASES:

    for key, value in dict.items():
        response = requests.get(BASE_URLS['Cases'].format("1") + CASES_KEYS[key] + ENDPOINTS['Cases'])

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_table(soup)

        data = pandas.DataFrame(res, columns=['Case Number', 'Defendant\'s Name', 'Offence Date', 'Local Authority', 'Main Activity'])

        data['Time-st'] = pandas.to_datetime('today').utcnow()

        try:
            os.makedirs('Cases/' + key)
        except FileExistsError:
            pass

        data.head(10).to_csv(f'Cases/{key}/{key}.csv', index=False)

        for i in range(2, get_pages_number(soup) + 1):
            response = requests.get(BASE_URLS['Cases'].format(i) + CASES_KEYS[key] + ENDPOINTS['Cases'])
            soup = BeautifulSoup(response.text, 'lxml')
            res = parse_table(soup)
            data = pandas.DataFrame(res, columns=['Case Number', 'Defendant\'s Name', 'Offence Date', 'Local Authority',
                                                  'Main Activity'])
            data['Time-st'] = pandas.to_datetime('today').utcnow()

            data.head(10).to_csv(f'Cases/{key}/{key}.csv', index=False, mode='a', header=False)

