import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from itertools import product
from tqdm import tqdm
from itertools import groupby
import PySimpleGUI as sg

bar_format = "{l_bar}{bar}{r_bar}"
tqdm.pandas(bar_format=bar_format)

def parse_range(input_range):
    result = []
    for part in input_range:
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.extend(range(start, end + 1))
        else:
            result.append(int(part))
    return result

def get_company_data(company_ids, year_range, month_range):
    data = []

    total_iterations = len(company_ids) * len(year_range) * len(month_range)

    for combination in tqdm(product(company_ids, year_range, month_range), total=total_iterations, desc="Processing", colour='green'):
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
        sorted_data = sorted(company_data, key=lambda x: (x['公司代號'], x['月份']))

        layout = [
            [sg.Text('公司代號（以逗號分隔）'), sg.InputText(key='company_ids')],
            [sg.Text('年份範圍（以逗號分隔或使用範圍符號 "-"）'), sg.InputText(key='year_range')],
            [sg.Text('月份範圍（以逗號分隔或使用範圍符號 "-"）'), sg.InputText(key='month_range')],
            [sg.Button('確認')],
            [sg.Table(values=[], headings=['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)', '月份'],
                      auto_size_columns=False, justification='right', key='table',
                      col_widths=[15, 30, 15, 15, 15, 20, 20, 15],
                      row_height=30, display_row_numbers=False, bind_return_key=True, enable_events=True, num_rows=20)],
            [sg.Text('每年度的平均當月營收:', key='average_text')],
        ]

        window = sg.Window('公司資料查詢工具', layout, resizable=True, finalize=True)

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED:
                break
            elif event == '確認':
                # Parsing input
                company_ids_input = [company_id.strip() for company_id in values['company_ids'].split(',')]
                year_range_input = values['year_range'].split(',')
                month_range_input = values['month_range'].split(',')

                # Converting to integers
                year_range = parse_range(year_range_input)
                month_range = parse_range(month_range_input)

                # Calling the function to get company data
                company_data = get_company_data(company_ids_input, year_range, month_range)

                # Sorting and printing company data
                sorted_data = sorted(company_data, key=lambda x: (x['公司代號'], x['月份']))

                table_data = []
                yearly_data = {year: [] for year in range(year_range[0], year_range[1] + 1)}

                for company_id, group in groupby(sorted_data, key=lambda x: x['公司代號']):
                    group = list(group)

                    for i, company in enumerate(group):
                        values_basic = [company.get(label, '') for label in ['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)']]  # 不包含 '月份'
                        values_basic.append(company.get('月份', ''))  # 添加 '月份'
                        table_data.append(values_basic)

                        if i == len(group) - 1:
                            # 添加空行，用於區分不同公司的數據
                            table_data.append([""] * len(table_data[0]))

                        # 計算每年度的平均值
                        year = int(company['月份'].split('-')[0])
                        yearly_data[year].append(float(company['當月營收'].replace(',', '')))

                    # 插入每年度的平均值行
                    for year, revenues in yearly_data.items():
                        if revenues:  # 避免除以零
                            average_revenue = sum(revenues) / len(revenues)
                            table_data.append(["", "", f"{average_revenue:.2f}", "", "", "", "", f"{year}年 平均值"])

                window['table'].update(values=table_data)

                # 輸出每年度的平均值
                avg_text = ""
                for year, revenues in yearly_data.items():
                    if revenues:  # 避免除以零
                        average_revenue = sum(revenues) / len(revenues)
                        avg_text += f"{year}年: {average_revenue:.2f}\n"

                window['average_text'].update(avg_text)

        window.close()

# PySimpleGUI used for creating the graphical interface
layout = [
    [sg.Text('公司代號（以逗號分隔）'), sg.InputText(key='company_ids')],
    [sg.Text('年份範圍（以逗號分隔或使用範圍符號 "-"）'), sg.InputText(key='year_range')],
    [sg.Text('月份範圍（以逗號分隔或使用範圍符號 "-"）'), sg.InputText(key='month_range')],
    [sg.Button('確認')],
    [sg.Table(values=[], headings=['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)', '月份'],
              auto_size_columns=False, justification='right', key='table',
              col_widths=[15, 30, 15, 15, 15, 20, 20, 15],
              row_height=30, display_row_numbers=False, bind_return_key=True, enable_events=True, num_rows=20)]
    
]

window = sg.Window('公司資料查詢工具', layout, resizable=True, finalize=True)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == '確認':
        # Parsing input
        company_ids_input = [company_id.strip() for company_id in values['company_ids'].split(',')]
        year_range_input = values['year_range'].split(',')
        month_range_input = values['month_range'].split(',')

        # Converting to integers
        year_range = parse_range(year_range_input)
        month_range = parse_range(month_range_input)

        # Calling the function to get company data
        company_data = get_company_data(company_ids_input, year_range, month_range)

        # Sorting and printing company data
        sorted_data = sorted(company_data, key=lambda x: (x['公司代號'], x['月份']))

        table_data = []
        yearly_data = {year: [] for year in range(year_range[0], year_range[1] + 1)}

    for company_id, group in groupby(sorted_data, key=lambda x: x['公司代號']):
        group = list(group)

        for i, company in enumerate(group):
            values_basic = [company.get(label, '') for label in ['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)']]  # 不包含 '月份'
            values_basic.append(company.get('月份', ''))  # 添加 '月份'
            table_data.append(values_basic)

            if i == len(group) - 1:
                # 添加空行，用於區分不同公司的數據
                table_data.append([""] * len(table_data[0]))

        # 計算每年度的平均值
        yearly_data = {year: [] for year in range(year_range[0], year_range[1] + 1)}
        for company in group:
            year = int(company['月份'].split('-')[0])
            yearly_data[year].append(float(company['當月營收'].replace(',', '')))

        # 插入每年度的平均值行
        for year, revenues in yearly_data.items():
            if revenues:  # 避免除以零
                average_revenue = sum(revenues) / len(revenues)
                table_data.append(["", "", f"{average_revenue:.2f}", "", "", "", "", f"{year}年 平均值"])

    window['table'].update(values=table_data)


window.close()
