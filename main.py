import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = pd.read_csv('data/TWTR.csv')
data['Date'] = pd.to_datetime(data['Date'], format="%Y-%m-%d")
data = data.set_index(data['Date'])
data = data.drop(columns=['Date'])


# Strategija
p1 = 20
p2 = 70

data_close = data['Close'].to_frame()
data_close['SMA20'] = data_close['Close'].rolling(20).mean()
data_close['SMA70'] = data_close['Close'].rolling(70).mean()

fig, ax = plt.subplots(2, 1, sharex=True, sharey=False)
ax[0].plot(data_close[['Close', 'SMA20', 'SMA70']])

np_sma20 = data_close['SMA20'].to_numpy()
np_sma70 = data_close['SMA70'].to_numpy()

idx = (np_sma20[1:] > np_sma70[1:]) != (np_sma20[:-1] > np_sma70[:-1])
idx = np.insert(idx, 0, False)

ax[0].scatter(data.index[idx], data_close['SMA20'][idx], marker='x', color='black')
ax[0].legend(['Close kaina', 'SMA20', 'SMA70'])

data['SMA20'] = data['Close'].rolling(20).mean()
data['SMA70'] = data['Close'].rolling(70).mean()

data['SMA20'] = data['SMA20'].fillna(0)
data['SMA70'] = data['SMA70'].fillna(0)

# Pozicijos


data['Future_Position'] = 0
data.loc[data['SMA20'] > data['SMA70'], 'Future_Position'] = 1
data.loc[data['SMA20'] < data['SMA70'], 'Future_Position'] = -1
data.loc[0:np.max([p1, p2]) - 1, 'Future_Position'] = 0

data['Position'] = data['Future_Position'].shift(1)
data.iloc[0, data.columns.get_loc('Position')] = 0

basis = data['Close'][0]
take_profit = basis * 1.15
stop_loss = basis * 0.6

""" 
for i in range(0, len(data)):
    if (data.iloc[i]['Close'] > take_profit):
        take_profit = basis * 1.15
        stop_loss = basis * 1.15
        ax[0].scatter(data.index[i], data_close['SMA20'][i], marker='o', color='yellow')
        basis = basis * 1.15
        print('Take profit')
    if (data.iloc[i]['Close'] < stop_loss):
        stop_loss = basis * 0.6
        take_profit = basis * 0.6
        ax[0].scatter(data.index[i], data_close['SMA20'][i], marker='o', color='blue')
        basis = basis * 1.15
        print('Stop loss')

"""
data['Position_Change'] = data['Future_Position'] != data['Position']

taxes = 0.15
data['Taxes'] = data['Position_Change'] * taxes * 2

data['Price_Diff'] = data['Close'].diff(1)
data.iloc[0, data.columns.get_loc('Price_Diff')] = 0

data['Profit_from_Position'] = data['Price_Diff'] * data['Position']
data['Gross_Profit'] = data['Profit_from_Position'] + data['Taxes']

gross_profit = np.cumsum(data['Gross_Profit'])
ax[1].plot(gross_profit)
