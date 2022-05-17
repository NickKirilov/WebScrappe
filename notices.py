import os
import pandas
import requests
from bs4 import BeautifulSoup
from common_utils import BASE_URLS, parse_notices_details_table


def scrap_notices():

        df = pandas.read_html(BASE_URLS['Notices'].format("1"), header=0)
        df[0]['Time-st'] = pandas.to_datetime('today').utcnow()

        data = df[0][
            ['Notice Number', 'Recipient\'s Name', 'Notice Type', 'Issue Date', 'Local Authority', 'Main Activity',
             'Time-st']]

        try:
            os.makedirs('Notices')
        except FileExistsError:
            pass

        data.head(10).to_csv(f'Notices/notices.csv', index=False)

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
            df = pandas.read_html(BASE_URLS['Notices'].format(i), header=0)
            df[0]['Time-st'] = pandas.to_datetime('today').utcnow()
            df[0].drop(df[0].tail(1).index, inplace=True)

            data = df[0]
            data.head(10).to_csv(f'Notices/notices.csv', index=False, mode='a', header=False)


def scrap_notices_details():

    df = pandas.read_csv(f'Notices/notices.csv', sep='\t')

    for i in range(0, len(df)):
        notice_number = df.iat[i, 0].split(',')[0]
        response = requests.get('https://resources.hse.gov.uk/notices/notices/notice_details.asp?SF=CN&SV=' + notice_number)

        soup = BeautifulSoup(response.text, 'lxml')
        res, col = parse_notices_details_table(soup)

        res.insert(0, df.iat[i, 0].split(',')[3])
        res.insert(0, df.iat[i, 0].split(',')[1])
        res.insert(0, notice_number)

        try:
            new_df = pandas.DataFrame(
                [res],
                columns=[
                    'Notice Number', 'Recipient Name', 'Served Date',
                ] + col
            )
            new_df['Time-st'] = pandas.to_datetime('today').utcnow()

            new_df.head(10).to_csv(f'Notices/{notice_number}.csv', index=False)
        except:
            print('Notice number: ' + notice_number)
            print('Could not create a dataframe')
            return
