import re

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
    'Notices': 'https://resources.hse.gov.uk/notices/notices/notice_list.asp?PN={}&ST=N&CO=&SN=F&SF=NN%2C+%7C&EO=LIKE&SV=%2C+%7C&SO=DNIS',
    'Cases': 'https://resources.hse.gov.uk/convictions/case/case_list.asp?PN={}&ST=C&CO=&SN=F&SF=CN%2C+%7C&EO=LIKE&SV=%2C+%7C&SO=ADN',
    'Breaches': 'https://resources.hse.gov.uk/convictions/breach/breach_list.asp?PN={}&ST=B&CO=&SN=F&SF=BID%2C+%7C&EO=LIKE&SV=%2C+%7C&SO=DHD'
}


def get_pages_number(soup):
    total_items = soup.find_all('p')
    matches = re.findall(r'Showing Page 1 of [0-9]+', total_items[2].text)

    if not len(matches):
        total_items = soup.find_all('th', attrs={'colspan': "5"})
        if not len(total_items):
            total_items = soup.find_all('th', attrs={'colspan': "6"})
        matches = re.findall(r'Showing Page 1 of [0-9]+', total_items[0].text)

    number = ''
    for i in range(len(matches[0])-1, 0, -1):
        if not matches[0][i].isdigit():
            break
        number += matches[0][i]

    return int(number[::-1])


def parse_cases_table(soup):
    table = soup.find_all('tr')
    res = []

    for tr in table:
        td = tr.find_all('td')
        row = [tr.text.strip() for tr in td if tr.text.strip()]
        if row:
            res.append(row)

    return res


def parse_notices_details_table(soup):
    table = soup.find_all('td')
    res = []

    for i in range(0, len(table)):

        try:
            if 'Breaches involved in this Notice' in table[i].text or 'HSE Details' in table[i].text:
                continue

            if i < 10 or i > 23:
                if i % 2 != 0:
                    res.append(table[i].text)
            else:
                if i % 2 == 0:
                    res.append(table[i].text)

        except IndexError:
            return res

    return res


def parse_cases_details_table(soup):
    table = soup.find_all('td')
    res = []

    for i in range(0, len(table)):

        try:
            if 'Breach involved in this Notice' in table[i].text or 'HSE Details' in table[i].text or 'Location of Offence' in table[i].text:
                continue

            if i > 24:
                if i % 2 == 0:
                    res.append(table[i].text)
            else:
                if i % 2 != 0:
                    res.append(table[i].text)

        except IndexError:
            return res

    return res


def parse_breaches_details_table(soup):
    table = soup.find_all('td')
    res = []

    fields_to_not_enter = [12, 13, 16, 17, 20, 21]

    for i in range(0, len(table)):

        try:
            if 'Case Details' in table[i].text or 'HSE Details' in table[i].text or 'Location of Offence' in table[i].text:
                continue

            if i in fields_to_not_enter:
                continue

            if i % 2 != 0:
                res.append(table[i].text)

        except IndexError:
            return res

    return res
