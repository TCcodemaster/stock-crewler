# 爬蟲實作-TWSE公開資料觀測站 
[Markdown Live Preview](https://hackmd.io/_uploads/ryd1UIhB6.png)

## 來源網站
[公開資訊觀測站 - 臺灣證券交易所](https://mops.twse.com.tw/mops/web/index)
* 爬取資源 :採用IFRSs後每月營業收入彙總表
![image](https://hackmd.io/_uploads/ryYGn8nS6.png)


## 前言
當你手上持有一支股票的時候，應該除了會時常看盤關注股價漲跌，也會想關注這家公司最近是否有在賺錢，最直接就是看公司的月營收，在**公開資訊觀測站 - 臺灣證券交易所**裡面可以查到上市上櫃歷年來目前為止的每個月營收，但當你手上有十支股票時，你必須在一張表格找十次，且每個月都要做一次，是否有點麻煩? 身為懶人的我決定透過程式來讓我一鍵產生我想要報表


 ## 事先準備
在這邊我用到就是PYTHON的爬蟲，並且運用一些套件讓我可以將資訊呈現成圖表
* **requests**: 用於發送HTTP請求，通常用於從網頁獲取資料。

* **bs4 (BeautifulSoup)**: 用於解析HTML和XML文件，提供簡單而直覺的方法來導覽和檢索網頁資料。

* **PrettyTable**: 用於將資料以表格形式輸出，使輸出更加可讀。


* **matplotlib.pyplot**: 用於繪製各種圖表和視覺化。

* **PySimpleGUI**: 一個簡單而直覺的GUI（圖形用戶界面）框架，用於建立基本的圖形界面應用程式。

* 可以先執行以下命令確保之後運行順利
```BASH=
pip install requests beautifulsoup4 prettytable tqdm matplotlib PySimpleGUI

```


## 📋1.取得資料 
#### 1.解析網頁，著尋目標
* 想要透過爬蟲得到資訊第一步一定是去分析HTML(網頁結構)，找出你需要資訊的段落，再根據網頁的TAG 做指定，於是就先去分析HTML找出我們感興趣的
    
  ![image](https://hackmd.io/_uploads/BygvAvnS6.png)
:::warning
可以看到我們想要爬取的表格在第三層的TABLE裡面，是屬於巢狀表格的結構
:::

* (當然也可以匯出成CSV，透過網址自動匯出CSV，之後的工作就會是針對工作表去做解析，比較不需要解決網頁結構HTML問題)
#### 2.爬取目標資訊
* 一般爬蟲的做法都是藉由標籤 (Tag) 來定位，透過搭配指定屬性(ID、CLASS)可以確保找到指定段落， **但是巢狀結構，不建議使用標籤屬性定位來爬取**，因為有可能可以第一個表格，但第二個就抓不到
* 關於如何爬我會先這樣寫 ，去測試是否抓到某公司的單筆數據


1. 發送 HTTP 請求、並定義了一個函數 `get_company_basic_data`，接受兩個參數(company_id 是要搜索的公司ID，url 是要爬取的網頁的URL)，初始化一個空字典 data 來存放爬取到的數據。
```python=
import requests
from bs4 import BeautifulSoup

def def get_company_basic_data(company_id, url):
    資料 = {}

    try:
        # 發送 HTTP 請求
        回應 = requests.get(url)
        回應.raise_for_status()  # 如果請求不成功，會拋出異常

```
2. 使用 `find('table')` 找到 HTML 中的第一個"table"標籤，即目標巢狀表格，再透過使用` find_all('td')` 找到每一行中的所有列，確保該行包含數據而不是空行，接者就可以對每一列的每一個單元格進行提取
    
```python=
        # 使用 BeautifulSoup 解析 HTML 內容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到指定的表格
        target_table = soup.find('table')

        # 提取表格中的數據
        if target_table:
            rows = target_table.find_all('tr')[2:]  # 忽略前兩行，因為它們是表頭

            for row in rows:
                columns = row.find_all('td')
                if columns:  # 確保這是一行數據，而不是空行
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

                        return data  # 返回找到的數據

    except requests.RequestException as e:
        print(f"錯誤: {e}")

    # 如果找不到指定公司ID的數據，返回None或者拋出異常，視情況而定
    return None
```
3. 使用 `get_company_basic_data` 函數爬取特定公司ID的數據，
    
```python=
company_id_to_search = '1101'  # 替換為你要搜索的公司ID
url_to_scrape = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_111_2_0.html'
result = get_company_basic_data(company_id_to_search, url_to_scrape)

if result:
    print(result)
else:
    print(f"未找到公司ID為{company_id_to_search}的數據。")
```
4.可以看到順利得到結果
![image](https://hackmd.io/_uploads/r1TNvshHa.png)


## 📋2.控制輸入及資料輸出
#### 1. 解析網址特性，參數化
* 我們可以透過網址觀察*https://mops.twse.com.tw/nas/t21/sii/t21sc03_111_2_0.html* 其實我們只要換掉111及02並設定成參數， 就可以爬取任何我們想要的年份及資料，且同時我會將月份及年度設定成範圍，這樣透過for迴圈就可以一次爬取很多年的資料，將我們要的參數設成輸入，這樣就可以自由控制參數，以下是我們的  **主程式碼**

:::info
輸入格式ex : id(2330)year(111,112)month(1,3)，就可以得到2330(TSMC)的111-112年1-3月的資料囉
<為了方便，自己創造的輸入code :+1: >
:::
```python=
#主程式碼
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
```
* 將 https://mops.twse.com.tw/nas/t21/sii/t21sc03_111_2_0.html 改成`https://mops.twse.com.tw/nas/t21/sii/t21sc03_{year}_{month}_0.html ` 並依序執行可能輸入組合，並調用上面提到的 ```get_company_basic_data ```函數爬取該公司指定月份的營收數據，如果有數據，則將數據加入到 data 列表中。
```python=
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
```
#### 2.資料輸出
* 若有多筆資料從字典印出會不易閱讀，所以輸出我採用建立一個 PrettyTable 物件來以表格呈現 ，並且按公司代號排序，方便閱讀
```python=
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
```
* 只是從網站印出原始資料似乎有點無聊吧，於是我就額外產生每年度的營收平均值透過我們產生的資料
:::warning
記得要放在```for company_id, group in groupby(sorted_data, key=lambda x: x['公司代號']):``` 迴圈裡面
:::
```python=
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
```
* 最後，只要在**主程式碼**呼叫函式就可以了

```python=
company_data = get_company_data(company_ids_input, year_range, month_range)
 # 印出公司資料
print_results(company_data)
```
:::success
input : id(2330)year(111,112)month(1,3)
:::
![image](https://hackmd.io/_uploads/SJtQwWk8p.png)
      

## 📋3. 包裝成GUI
* 因為若要時常使用，終端機的介面還是不太適合，所以我採用PySimpleGUI 布局，並將輸入分為三個輸入框:公司代號、年份範圍、月份範圍，同時會有input_log的設定這樣下次進來就會記得上次輸入的組合
#### 1.介面基礎設計
:::warning
因為介面都是顯示在PySimpleGUI，所以上面提到 print_results的部分就可以刪除
:::
* 保存輸入進log以及PySimpleGUI layout
```python=

def parse_range(input_range):
    result = []
    for part in input_range:
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.extend(range(start, end + 1))
        else:
            result.append(int(part))
    return result

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
    [sg.Text('年份範圍（使用範圍符號 "-"）'), sg.InputText(key='year_range')],
    [sg.Text('月份範圍（使用範圍符號 "-"）'), sg.InputText(key='month_range')],
    [sg.Button('確認'),  sg.Button('離開並儲存搜尋紀錄', key='leave')],
    [sg.Table(values=[], headings=['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)', '月份'],
              auto_size_columns=False, justification='right', key='table',
              col_widths=[15, 30, 15, 15, 15, 20, 20, 15],
              row_height=30, display_row_numbers=False, bind_return_key=True, enable_events=True, num_rows=20)],
]

window = sg.Window('公司資料查詢工具', layout, resizable=True, finalize=True)
```
* 主程式事件設定
```python=
# 主循環
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == '離開':
        if values is not None:
            # 在退出時保存輸入紀錄到檔案
            input_log = read_input_log(input_log_file)
            current_input = f"公司代號:{values['company_ids']}, 年份範圍:{values['year_range']}, 月份範圍:{values['month_range']}"
            if current_input not in input_log:
                input_log.append(current_input)
                save_input_log(input_log_file, input_log)
        break
    elif event == '填入':
        # 解析選擇的過去紀錄
        selected_input = values['saved_inputs']
        if selected_input:
            selected_input_dict = parse_input_record(selected_input)

            # 更新每個輸入字段的值
            for key, value in selected_input_dict.items():
                window[key].update(value)
    elif event == '確認':
        # 轉換input成為列表供parse_range使用
        company_ids_input = [company_id.strip() for company_id in values['company_ids'].split(',')]
        year_range_input = [values['year_range']]
        month_range_input = [values['month_range']]

        # 轉換為整數
        year_range = parse_range(year_range_input)
        month_range = parse_range(month_range_input)

        # 調用獲取公司數據的函數
        company_data = get_company_data(company_ids_input, year_range, month_range)

        # 排序並打印公司數據
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

                # 檢查 year 是否在 yearly_data 的鍵中，如果不在，添加它
                if year not in yearly_data:
                    yearly_data[year] = []

                yearly_data[year].append(float(company['當月營收'].replace(',', '')))

            # 插入每年度的平均值行
            for year, revenues in yearly_data.items():
                if revenues:  # 避免除以零
                    average_revenue = sum(revenues) / len(revenues)
                    table_data.append(["", "", f"{average_revenue:.2f}", "", "", "", "", f"{year}年 平均值"]

```
* 介面呈現
![image](https://hackmd.io/_uploads/BkyzlBxLp.png)

#### 2.產生折線圖
* 表格對於若我同時搜尋多家公司或多個年度，要去比較時其實不太方便，所以我額外產生三個按鈕來產生折線圖，分別是 **不同公司營收圖**、**歷年營收比較** 、**營收增減%圖**
* 先在layout增加按鈕
```pythom=
[sg.Button('不同公司營收圖', key='plot_button'),sg.Button('歷年營收比較', key='time_button'),sg.Button('營收增減%圖', key='rate_button')], 
```


---

1. 不同公司營收圖 、營收增減%圖
    這兩張圖的產生邏輯相同，只是抓取不同欄位，故我一起說明，
:::info
1. 取得表格資料： 從界面中的表格元素中取得資料。
2. 資料處理： 將表格資料按照公司代號（'公司代號'）進行分組（使用 groupby 函式），並按照年份月份（'月份'）進行排序。
3. 製作繪圖所需的資料： 創建一個字典 plot_data，用於存儲每家公司的月份和營收數據。
4. 繪製折線圖： 對於每家公司，將其營收數據加入 plot_data 字典中，然後使用 plt.plot 函式繪製折線圖。
* 將```'營收'```替換程```'營收增減(%)'```就可以完成營收增減%圖
:::

```python=
    elif event == 'plot_button':
        table_data = window['table'].get()

        if table_data and table_data[0]:
            plt.figure(figsize=(10, 6))
            plot_data = {company_id: {'月份': [], '營收': []} for company_id in company_ids_input}

            for company_id, group in groupby(sorted_data, key=lambda x: x['公司代號']):
                group = list(group)

                for i, company in enumerate(group):
                    # 計算每年度的值
                    year = int(company['月份'].split('-')[0])
                    month = int(company['月份'].split('-')[1])
                    plot_data[company_id]['月份'].extend([f"{year}-{month:02d}"])
                    plot_data[company_id]['營收'].extend([float(company['當月營收'].replace(',', ''))])

            for company_id, data in plot_data.items():
                plt.plot(data['月份'], data['營收'], label=f"{company_id} 平均值")

            plt.xlabel('時間', fontproperties=font1, fontsize=20)
            plt.ylabel('營收', fontproperties=font1, fontsize=20)
            plt.title('年度營收折線圖', fontproperties=font1, fontsize=20)
            plt.xticks(rotation=45)  # 旋轉 x 軸標籤，以免重疊
            plt.legend(prop=font1)
            plt.grid(True)
            plt.ticklabel_format(axis='y', style='plain') 
            plt.tight_layout()  # 自動調整佈局，以確保標籤完全顯示
            plt.show()
        else:
            sg.popup_error('表格無資料，請先點擊「確認」獲取數據。')
```
* **成果!**

![image](https://hackmd.io/_uploads/HJHVYBg86.png)


2. 歷年營收比較
* 這張圖比較不一樣，他是只會看一家公司的數據，但可以在月份的軸上看到多個月的比較，可以去比較同時期去年度的表現，
* 所以他是透過year_data去分類
:::info
1. 過濾選擇公司的資料： 從整體資料中篩選出選擇公司的相關資料。
2. 製作繪圖所需的資料： 創建一個字典 years_data，用於存儲該公司不同年度的月份和營收數據。
3. 繪製折線圖： 對於每年份，將其營收數據加入 years_data 字典中，然後使用 plt.plot 函式繪製折線圖。
:::
```python
    elif event == 'time_button':
        # Get selected company ID
        selected_company_id = values['company_ids'].split(',')[0].strip()

        # Filter data for the selected company
        selected_company_data = [company for company in sorted_data if company['公司代號'] == selected_company_id]

        if selected_company_data:
            plt.figure(figsize=(10, 6))

            # Organize data for plotting
            years_data = {str(year): {'月份': [], '營收': []} for year in range(year_range[0], year_range[1] + 1)}

            for company in selected_company_data:
                year = int(company['月份'].split('-')[0])
                month = int(company['月份'].split('-')[1])

                # Ensure the year key exists in the dictionary
                if str(year) not in years_data:
                    years_data[str(year)] = {'月份': [], '營收': []}

                years_data[str(year)]['月份'].append(f"{month:02d}")
                years_data[str(year)]['營收'].append(float(company['當月營收'].replace(',', '')))

            # Plotting for each year
            for year, data in years_data.items():
                plt.plot(data['月份'], data['營收'], label=f"{year} 年")
            plt.xlabel('月份', fontproperties=font1, fontsize=20)
            plt.ylabel('營收', fontproperties=font1, fontsize=20)
            plt.title(f"{selected_company_id} 不同年度營收折線圖", fontproperties=font1, fontsize=20)
            plt.xticks(rotation=45)
            plt.legend(prop=font1)
            plt.grid(True)
            plt.ticklabel_format(axis='y', style='plain')
            plt.tight_layout()
            plt.show()
 
        else:
            sg.popup_error(f'選擇的公司（ID: {selected_company_id}）無相關數據，請嘗試其他公司。')
 
```

* **成果!**
![image](https://hackmd.io/_uploads/HytHKSg8T.png)

:::danger
折線圖的中文字型要另外下載並引用，不然無法顯示
:::
