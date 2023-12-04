import requests
from bs4 import BeautifulSoup
from itertools import groupby, product
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from matplotlib.font_manager import FontProperties as font
from tqdm import tqdm
import os  # 引入 os 模組

# 指定檔案路徑
input_log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'input_log.txt')

# 其他程式碼不變

font1 = font(fname=r"C:\Users\raising.2201.DESKTOP-OIFBBUJ\Downloads\Noto_Sans_TC\NotoSansTC-VariableFont_wght.ttf")

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

                        # Ensure '月份' 存在
                        if '月份' in data:
                            data['月份'] = f'{year}-{month:02d}'

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



def read_input_log(file_path):
    # 讀取過去的五筆紀錄
    input_log = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines[-5:]:  # 只取最後五筆
                input_log.append(line.strip())
    except FileNotFoundError:
        pass
    return input_log

def save_input_log(file_path, input_log):
    # 將最新的輸入保存到檔案
    with open(file_path, 'a') as file:
        file.write('\n'.join(input_log) + '\n')

def parse_input_record(record):
    # 解析輸入紀錄為字典
    parsed_record = {}
    parts = record.split(',')
    for part in parts:
        key, value = map(str.strip, part.split(':'))
        parsed_record[key] = value
    return parsed_record

# PySimpleGUI 布局
layout = [
    [sg.Text('請選擇過去的五筆紀錄')],[sg.Button('填入')],
    [sg.DropDown(values=read_input_log(input_log_file), key='saved_inputs')],
    [sg.Text('公司代號（以逗號分隔）'), sg.InputText(key='company_ids')],
    [sg.Text('年份範圍（以逗號分隔或使用範圍符號 "-"）'), sg.InputText(key='year_range')],
    [sg.Text('月份範圍（以逗號分隔或使用範圍符號 "-"）'), sg.InputText(key='month_range')],
    [sg.Button('確認'), sg.Button('生成折線圖', key='plot_button'), sg.Button('離開', key='leave')],
    [sg.Table(values=[], headings=['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)', '月份'],
              auto_size_columns=False, justification='right', key='table',
              col_widths=[15, 30, 15, 15, 15, 20, 20, 15],
              row_height=30, display_row_numbers=False, bind_return_key=True, enable_events=True, num_rows=20)],
]

window = sg.Window('公司資料查詢工具', layout, resizable=True, finalize=True)


while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'leave':
        if values is not None:
            # 在退出時保存輸入紀錄到檔案
            input_log = read_input_log(input_log_file)
            current_input = f"company_ids:{values['company_ids']}, year_range:{values['year_range']}, month_range:{values['month_range']}"
            if current_input not in input_log:
                input_log.append(current_input)
                save_input_log(input_log_file, input_log)
        break
    elif event == '填入':
                # 解析選擇的過去紀錄
        selected_input = values['saved_inputs']
        if selected_input:
            selected_input_dict = parse_input_record(selected_input)

            # Update the values for each input field individually
            for key, value in selected_input_dict.items():
                window[key].update(value)
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
                
                # 检查 year 是否在 yearly_data 的键中，如果不在，添加它
                if year not in yearly_data:
                    yearly_data[year] = []

                yearly_data[year].append(float(company['當月營收'].replace(',', '')))

            # 插入每年度的平均值行
            for year, revenues in yearly_data.items():
                if revenues:  # 避免除以零
                    average_revenue = sum(revenues) / len(revenues)
                    table_data.append(["", "", f"{average_revenue:.2f}", "", "", "", "", f"{year}年 平均值"])

        window['table'].update(values=table_data)

    elif event == 'plot_button':
        table_data = window['table'].get()

        if table_data and table_data[0]:
            plt.figure(figsize=(10, 6))
            plot_data = {company_id: {'月份': [], '營收': []} for company_id in company_ids_input}

            for company_id, group in groupby(sorted_data, key=lambda x: x['公司代號']):
                group = list(group)

                for i, company in enumerate(group):
                    # 計算每年度的平均值
                    year = int(company['月份'].split('-')[0])
                    month = int(company['月份'].split('-')[1])
                    plot_data[company_id]['月份'].extend([f"{year}-{month:02d}"])
                    plot_data[company_id]['營收'].extend([float(company['當月營收'].replace(',', ''))])

            for company_id, data in plot_data.items():
                plt.plot(data['月份'], data['營收'], label=f"{company_id} 平均值")

            plt.xlabel('時間', fontproperties=font1, fontsize=20)
            plt.ylabel('平均營收', fontproperties=font1, fontsize=20)
            plt.title('年度營收折線圖', fontproperties=font1, fontsize=20)
            plt.xticks(rotation=45)  # 旋轉 x 軸標籤，以免重疊
            plt.legend(prop=font1)
            plt.grid(True)
            plt.ticklabel_format(axis='y', style='plain') 
            plt.tight_layout()  # 自動調整佈局，以確保標籤完全顯示
            plt.show()
        else:
            sg.popup_error('表格無資料，請先點擊「確認」獲取數據。')


# Close the window when the event loop exits
window.close()