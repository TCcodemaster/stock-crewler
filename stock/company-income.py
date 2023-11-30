import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from itertools import product
from tqdm import tqdm
from itertools import groupby

bar_format = "{l_bar}{bar}{r_bar}"
tqdm.pandas(bar_format=bar_format)

def get_company_data(company_ids, year_range, month_range):
    data = []

    # 估算迴圈的總長度
    total_iterations = len(company_ids) * len(range(year_range[0], year_range[1] + 1)) * len(range(month_range[0], month_range[1] + 1))

    # 封裝成 tqdm
    for combination in tqdm(product(company_ids, range(year_range[0], year_range[1] + 1), range(month_range[0], month_range[1] + 1)),
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

    # 發送 HTTP 請求
    response = requests.get(url)

    # 檢查請求是否成功
    if response.status_code == 200:
        # 使用 BeautifulSoup 解析 HTML 內容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到指定的表格
        target_table = soup.find('table')

        # 提取表格中的資料
        if target_table:
            rows = target_table.find_all('tr')[2:]  # 忽略前兩行，因為它們是表頭

            for row in rows:
                columns = row.find_all('td')
                if columns:  # 確保這是一行資料，而不是空行
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

                        break  # 移到這裡，確保只在找到符合公司代號的資料後中斷迴圈

    return data


def print_results(company_data):
    if company_data:
        # 先按公司代號排序
        sorted_data = sorted(company_data, key=lambda x: x['公司代號'])

        # 印出表格的標籤
        table_basic = PrettyTable()
        table_basic.field_names = ['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)', '月份']

        # 顯示每筆資料
        for company_id, group in groupby(sorted_data, key=lambda x: x['公司代號']):
            group = list(group)

            for i, company in enumerate(group):
                # 顯示基本資料
                values_basic = [company.get(label, '') for label in table_basic.field_names[:-1]]  # 不包含 '月份'
                values_basic.append(company.get('月份', ''))  # 添加 '月份'
                table_basic.add_row(values_basic)

                if i == len(group) - 1:
                    print(f"基本資料 (公司代號: {company_id}):")
                    print(table_basic)

            # 計算每年度的平均值
            yearly_data = {year: [] for year in range(year_range[0], year_range[1] + 1)}
            for company in group:
                year = int(company['月份'].split('-')[0])
                yearly_data[year].append(float(company['當月營收'].replace(',', '')))

            # 輸出每年度的平均值
            print(f"每年度的平均當月營收:")
            for year, revenues in yearly_data.items():
                average_revenue = sum(revenues) / len(revenues)
                print(f"{year}年: {average_revenue:.2f}")

            # 清空表格
            table_basic.clear_rows()

# 主程式碼
while True:
    user_input = input('請輸入輸入code，或輸入 "q" 退出: ')
    if user_input.lower() == 'q':
        break
    else:
        # 解析輸入
        input_parts = user_input.split(')')
        company_ids_input = [company_id.strip() for company_id in input_parts[0].replace('id(', '').split(',')]
        year_range_input = input_parts[1].replace('year(', '').split(',')
        month_range_input = input_parts[2].replace('month(', '').replace(')', '').split(',')

        # 轉換為整數
        year_range = [int(year) for year in year_range_input]
        month_range = [int(month) for month in month_range_input]   

        # 輸出解析後的值（可選）
        print("公司代號:", company_ids_input)
        print("年份範圍:", year_range)
        print("月份範圍:", month_range)

        # 呼叫函式取得公司資料
        company_data = get_company_data(company_ids_input, year_range, month_range)

        # 印出公司資料
        print_results(company_data)
