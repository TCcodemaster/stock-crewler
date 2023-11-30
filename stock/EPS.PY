import twstock
import pandas as pd
import matplotlib.pyplot as plt
from pylab import mpl

# Dynamically input stock ID, year, and month
stock_id = input("Please enter stock ID: ")
year = input("Please enter the year: ")
month = input("Please enter the month: ")

# Fetch stock data
stock = twstock.Stock(stock_id)
stock_data = stock.fetch_from(int(year), int(month))

# Convert the fetched data into a DataFrame
df_stock_data = pd.DataFrame(stock_data, columns=['date', 'capacity', 'turnover', 'open', 'high', 'low', 'close', 'change', 'transaction'])
df_stock_data['date'] = pd.to_datetime(df_stock_data['date'])  # Convert 'date' to datetime format

# Plot the stock prices
plt.title(f'Stock Prices for {stock_id}', fontsize=24)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Price', fontsize=14)
plt.plot(df_stock_data['date'], df_stock_data['close'])
plt.show()
