import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def strategy_SMA(data, price_column_name, p1, p2, taxes):
    data['SMA20'] = data[price_column_name].rolling(p1).mean()
    data['SMA70'] = data[price_column_name].rolling(p2).mean()

    data['Future_Position'] = 0
    data.loc[data['SMA20'] > data['SMA70'], 'Future_Position'] = 1
    data.loc[data['SMA20'] < data['SMA70'], 'Future_Position'] = -1
    data.loc[0:np.max([p1, p2]) - 1, 'Future_Position'] = 0

    data['Position'] = data['Future_Position'].shift(1)
    data.iloc[0, data.columns.get_loc('Position')] = 0

    data['Position_Change'] = data['Future_Position'] != data['Position']

    data['Taxes'] = data['Position_Change'] * taxes * 2

    data['Price_Diff'] = data[price_column_name].diff(1)
    data.iloc[0, data.columns.get_loc('Price_Diff')] = 0

    data['Profit_from_Position'] = data['Price_Diff'] * data['Position']
    data['Gross_Profit'] = data['Profit_from_Position'] + data['Taxes']

    return data['Gross_Profit']

data = pd.read_csv('data/TWTR.csv')
data['Date'] = pd.to_datetime(data['Date'], format="%Y-%m-%d")
data = data.set_index(data['Date'])
data = data.drop(columns=['Date'])

p1 = 20
p2 = 70

df = data['Close'].copy()
price_column_name = 'Close'
taxes = -0.3



def Sharpe_Ratio(returns, N=252):
    return np.sqrt(N) * returns.mean() / returns.std()

df_optim = pd.DataFrame(columns=['p1', 'p2', 'Sharpe_Ratio', 'results'])

for p1 in range(1, 100, 2):
    for p2 in range(1, 100, 2):
        if p1 != p2:
            rez = strategy_SMA(df, 'Close', p1,p2, taxes)
            sharpe_ratio = Sharpe_Ratio(rez)
            df_optim = df_optim.append({'p1': p1, 'p2': p2, 'sharpe_ratio': sharpe_ratio, 'results': rez.copy()})

