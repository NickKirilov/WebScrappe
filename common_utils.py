BASE_URLS = {
    'Notices': 'https://resources.hse.gov.uk/notices/notices/notice_list.asp?PN={}&ST=N&CO=&SN=F&SF=NN%2C+%7C&EO=LIKE&SV=%2C+%7C&SO=DNIS',
    'Cases': 'https://resources.hse.gov.uk/convictions/case/case_list.asp?PN={}&ST=C&CO=&SN=F&SF=CN%2C+%7C&EO=LIKE&SV=%2C+%7C&SO=ADN',
    'Breaches': 'https://resources.hse.gov.uk/convictions/breach/breach_list.asp?PN={}&ST=B&CO=&SN=F&SF=BID%2C+%7C&EO=LIKE&SV=%2C+%7C&SO=DHD',
    'HistoricalBreaches': 'https://resources.hse.gov.uk/convictions-history/breach/breach_list.asp?PN={}&ST=B&CO=&SN=F&SF=BID%2C+%7C&EO=LIKE&SV=%2C+%7C&SO=DHD',
    'HistoricalCases': 'https://resources.hse.gov.uk/convictions-history/case/case_list.asp?PN={}&ST=C&CO=&SN=F&SF=CN%2C+%7C&EO=LIKE&SV=%2C+%7C&SO=ADN',
}


def parse_cases_breaches_table(soup):
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
    col = []
    if len(table) < 27:
        for i in range(0, len(table)):

            try:
                if 'Breaches involved in this Notice' in table[i].text or 'HSE Details' in table[i].text:
                    continue

                if i < 4 or i > 17:
                    if i % 2 != 0:
                        res.append(table[i].text)
                    else:
                        col.append(table[i].text)
                else:
                    if i % 2 == 0:
                        res.append(table[i].text)
                    else:
                        col.append(table[i].text)

            except IndexError:
                return res, col

    else:
        for i in range(0, len(table)):

            try:
                if 'Breaches involved in this Notice' in table[i].text or 'HSE Details' in table[i].text:
                    continue

                if i < 10 or i > 23:
                    if i % 2 != 0:
                        res.append(table[i].text)
                    else:
                        col.append(table[i].text)
                else:
                    if i % 2 == 0:
                        res.append(table[i].text)
                    else:
                        col.append(table[i].text)

            except IndexError:
                return res, col

    return res, col


def parse_cases_details_table(soup):
    table = soup.find_all('td')
    res = []

    for i in range(0, len(table)):

        try:
            if 'Breach involved in this Case' in table[i].text or 'HSE Details' in table[i].text or 'Location of Offence' in table[i].text:
                continue

            if 'This case did result' in table[5].text:
                if i % 2 != 0 and i <= 26:
                    res.append(table[i].text)
                else:
                    if i % 2 == 0 and i > 26:
                        res.append(table[i].text)
            elif i > 24:
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

            if i % 2 != 0 and i < 36:
                res.append(table[i].text)
            elif i % 2 == 0 and i > 36:
                res.append(table[i].text)

        except IndexError:
            return res

    return res

