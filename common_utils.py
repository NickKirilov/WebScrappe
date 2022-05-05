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


def parse_cases_table(soup):
    table = soup.find_all('tr')
    res = []

    for tr in table:
        td = tr.find_all('td')
        row = [tr.text.strip() for tr in td if tr.text.strip()]
        if row:
            res.append(row)

    return res


def parse_details_table(soup):
    table = soup.find_all('td')
    res = []

    for i in range(0, 10):
        try:
            if 'Breach involved in this Notice' in table[i].text:
                continue

            if i % 2 != 0:
                res.append(table[i].text)
        except IndexError:
            return res

    return res
