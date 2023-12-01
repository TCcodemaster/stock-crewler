import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from itertools import product
from tqdm import tqdm
from itertools import groupby
import PySimpleGUI as sg

bar_format = "{l_bar}{bar}{r_bar}"
tqdm.pandas(bar_format=bar_format)

def get_company_data(company_ids, year_range, month_range):
    data = []

    total_iterations = len(company_ids) * len(year_range) * len(month_range)

    for combination in tqdm(product(company_ids, year_range, month_range),
                            total=total_iterations, desc="Processing", colour='green'):
        company_id, year, month = combination
        url = f'https://mops.twse.com.tw/nas/t21/sii/t21sc03_{year}_{month}_0.html'
        company_data = get_company_basic_data(company_id, url)

        if company_data:
            company_data['月份'] = f'{year}-{month:02d}'
            data.append(company_data)

    return data

def get_company_basic_data(company_id, url):
    data = {}

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        target_table = soup.find('table')

        if target_table:
            rows = target_table.find_all('tr')[2:]

            for row in rows:
                columns = row.find_all('td')
                if columns:
                    fetched_company_id = columns[0].text.strip()
                    if fetched_company_id == company_id:
                        company_name = columns[1].text.strip().encode('latin-1').decode('big5', 'ignore')
                        monthly_revenue = columns[2].text.strip()
                        last_month_revenue = columns[3].text.strip()
                        last_year_month_revenue = columns[4].text.strip()
                        monthly_growth_rate = columns[5].text.strip()
                        last_year_growth_rate = columns[6].text.strip()

                        data = {
                            '公司代號': fetched_company_id,
                            '公司名稱': company_name,
                            '當月營收': monthly_revenue,
                            '上月營收': last_month_revenue,
                            '去年當月營收': last_year_month_revenue,
                            '上月比較增減(%)': monthly_growth_rate,
                            '去年同月增減(%)': last_year_growth_rate
                        }

                        break

    return data

def print_results(company_data):
    if company_data:
        sorted_data = sorted(company_data, key=lambda x: x['公司代號'])

        table_basic = PrettyTable()
        table_basic.field_names = ['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)', '月份']

        data_rows = []
        for company_id, group in groupby(sorted_data, key=lambda x: x['公司代號']):
            group = list(group)

            for i, company in enumerate(group):
                values_basic = [company.get(label, '') for label in table_basic.field_names[:-1]]
                values_basic.append(company.get('月份', ''))
                data_rows.append(values_basic)

            yearly_data = {year: [] for year in set(int(company['月份'].split('-')[0]) for company in group)}
            for company in group:
                year = int(company['月份'].split('-')[0])
                yearly_data[year].append(float(company['當月營收'].replace(',', '')))

            data_rows.append(["", "", "", "", "", "", "", ""])  # Add an empty row between companies

            for year, revenues in yearly_data.items():
                average_revenue = sum(revenues) / len(revenues)
                data_rows.append([f"{year}年平均當月營收:", "", "", "", "", "", f"{average_revenue:.2f}", ""])

        return data_rows

# PySimpleGUI used for creating the graphical interface
layout = [
    [sg.Text('公司代號（以逗號分隔）'), sg.InputText(key='company_ids')],
    [sg.Text('年份範圍（以逗號分隔）'), sg.InputText(key='year_range')],
    [sg.Text('月份範圍（以逗號分隔）'), sg.InputText(key='month_range')],
    [sg.Button('確認'), sg.Button('退出')],
    [sg.Table(values=[], headings=['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)', '月份'],
             auto_size_columns=False, justification='right', key='table',
              col_widths=[15, 30, 15, 15, 15, 20, 20, 15],
              row_height=30, display_row_numbers=False, bind_return_key=True, enable_events=True, num_rows=20)],
]

window = sg.Window('公司資料查詢工具', layout, resizable=True, finalize=True)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == '退出':
        break
    elif event == '確認':
        # Parsing input
        company_ids_input = [company_id.strip() for company_id in values['company_ids'].split(',')]
        year_range_input = values['year_range'].split(',')
        month_range_input = values['month_range'].split(',')

        # Converting to integers
        year_range = [int(year) for year in year_range_input] if year_range_input[0] else [int(year_range_input[0])]
        month_range = [int(month) for month in month_range_input] if month_range_input[0] else [int(month_range_input[0])]

        # Calling the function to get company data
        company_data = get_company_data(company_ids_input, year_range, month_range)

        # Printing company data
        table_data = print_results(company_data)

        # Update the table in the PySimpleGUI window
        window['table'].update(values=table_data)

window.close()
