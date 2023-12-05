import twstock
import pandas as pd
import mplfinance as mpf
import io
from tqdm import tqdm

def fetch_stock_data(target_stock, year, month):
    stock = twstock.Stock(target_stock)
    target_price = stock.fetch_from(year, month)
    return target_price

def save_to_io(df):
    csv_data = df.to_csv(index=False)
    return io.StringIO(csv_data)



def main():
    while True:
        # 使用者輸入
        target_stock = input("請輸入股票代號（例如：0050），輸入 'q' 退出：")
        
        # 檢查是否輸入 'q' 以退出迴圈
        if target_stock.lower() == 'q':
            break
        
        year_input = int(input("請輸入年份："))
        month_input = int(input("請輸入月份："))

        # 進度條設定
        with tqdm(total=50, desc="Fetching Stock Data", bar_format="{l_bar}{bar}{r_bar}", colour='red') as pb:
            target_price = fetch_stock_data(target_stock, year_input, month_input)
            pb.update(50)  # 模擬進度條更新

        # 資料整理
        name_attribute = ['Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change', 'Transcation']
        df = pd.DataFrame(columns=name_attribute, data=target_price)
        df.rename(columns={'Turnover': 'Volume'}, inplace=True)

        # 進度條設定
        with tqdm(total=100, desc="Saving to StringIO", bar_format="{l_bar}{bar}{r_bar}", colour='red') as pb:
            csv_buffer = save_to_io(df)
            pb.update(50)  # 模擬進度條更新

        # 股票走勢圖繪製
        df = pd.read_csv(csv_buffer, parse_dates=True, index_col=0)
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)

        kwargs = dict(type='candle', mav=(5, 20, 60), volume=True, figratio=(10, 8), figscale=0.75, title=target_stock, style=s)
        mpf.plot(df, **kwargs)

if __name__ == "__main__":
    main()
