import os
import pandas
import requests
from bs4 import BeautifulSoup
from common_utils import BASE_URLS, parse_cases_table, parse_cases_details_table


def scrape_cases():
        response = requests.get(BASE_URLS['Cases'].format("1"))

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_cases_table(soup)

        data = pandas.DataFrame(res, columns=['case_number', 'defendant\'s_name', 'offence_date', 'local_authority',
                                          'main_activity'])

        data['cytora_ingest_ts'] = pandas.to_datetime('today').utcnow()

        try:
            os.makedirs('Cases')
        except FileExistsError:
            pass

        data.head(10).to_csv(f'Cases/cases.csv', index=False)

        i = 2
        while True:

            response = requests.get(BASE_URLS['Cases'].format(i))
            soup = BeautifulSoup(response.text, 'lxml')

            res = parse_cases_table(soup)
            res.pop()

            if len(res) <= 0:
                print('No more cases to show.')
                return

            data = pandas.DataFrame(res,
                                    columns=['case_number', 'defendant\'s_name', 'offence_date', 'local_authority',
                                             'main_activity'])
            data['cytora_ingest_ts'] = pandas.to_datetime('today').utcnow()
            data.head(10).to_csv(f'Cases/cases.csv', index=False, mode='a', header=False)

            i += 1


def scrape_cases_details(cases: list = None):
    errors = set()
    errors_arr = []
    success = set()
    success_arr = []

    if cases:
        for i in range(0, len(cases)):
            case_number = cases[i].get('case_id')

            a = fetch_cases_details(case_number)

            if not a.get('state'):
                errors.add(a.get('case_id'))
                errors_arr.append(a)
            else:
                success.add(a.get('case_id'))
                success_arr.append(a)
    else:
        df = pandas.read_csv(f'Cases/cases.csv', sep='\t')

        for i in range(0, len(df)):
            case_number = df.iat[i, 0].split(',')[0]

            a = fetch_cases_details(case_number)

            if not a.get('state'):
                errors.add(a.get('case_id'))
                errors_arr.append(a)
            else:
                success.add(a.get('case_id'))
                success_arr.append(a)

    print('Errors: ' + str(errors))
    print('Successful: ' + str(success))
    print(len(success_arr))


def fetch_cases_details(case_id: str) -> dict:
    try:
        response = requests.get(
            'https://resources.hse.gov.uk/convictions/case/case_details.asp?SF=CN&SV=' + case_id)

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

        new_df['cytora_ingest_ts'] = pandas.to_datetime('today').utcnow()
        # TODO: must handle the following row
        file_path = f'Cases/{case_id}.csv'
        new_df.head(10).to_csv(file_path, index=False)

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


