import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'

twitter = pd.read_csv('data/TWTR.csv').set_index('Date')
twitter.index = pd.to_datetime(twitter.index)
twitter.tail()

twitter1 = twitter[['Close']].copy()

def SMA(data, window):
    sma = data.rolling(window = window).mean()
    return sma

def Bollinger_Bands(data, sma, window):
    std = data.rolling(window = window).std()
    upper_bb = sma + std * 2
    lower_bb = sma - std * 2
    return upper_bb, lower_bb

def strategy(data, window, taxes):
    data['SMA_20'] = SMA(data['Close'], window)
    data['SMA_20'] = data['SMA_20'].fillna(0)
    data.tail()

    data['Upper_BB'], data['Lower_BB'] = Bollinger_Bands(data['Close'], data['SMA_20'], window)
    data['Upper_BB'] = data['Upper_BB'].fillna(0)
    data['Lower_BB'] = data['Lower_BB'].fillna(0)
    data.tail()

    data['Future_Position'] = 0
    data['Position_Changed'] = False
    have_invested = 0

    for i in range(len(data)):
        if have_invested == 0:
        # Jeigu neturim nusipirke
            if data.iloc[i]['Close'] < data.iloc[i]['SMA_20'] and data.iloc[i]['Close'] > data.iloc[i]['Lower_BB']:
                data.iloc[i, data.columns.get_loc('Future_Position')] = 1
                have_invested = 1
            else:
                data.iloc[i]['Future_Position'] = 0
        else:
            if data.iloc[i]['Close'] > data.iloc[i]['Upper_BB']:
                data.iloc[i, data.columns.get_loc('Position_Changed')] = True
                data.iloc[i, data.columns.get_loc('Future_Position')] = 0
                have_invested = 0

            elif data.iloc[i]['Close'] < data.iloc[i]['Lower_BB']:
                data.iloc[i, data.columns.get_loc('Position_Changed')] = True
                data.iloc[i, data.columns.get_loc('Future_Position')] = 0
                have_invested = 0
            else:
                data.iloc[i, data.columns.get_loc('Future_Position')] = 1

    data['Taxes'] = data['Position_Changed'] * taxes * 1

    data['Price_Diff'] = data['Close'].diff(1)
    data.iloc[0, data.columns.get_loc('Price_Diff')] = 0

    data['Profit_from_Position'] = data['Price_Diff'] * data['Future_Position']
    data['Gross_Profit'] = data['Profit_from_Position'] + data['Taxes']

    return data['Gross_Profit']

def Sharpe_Ratio(returns, N=252):
    print(np.sqrt(N) * returns.mean() / (returns.std() + 0.01))
    return np.sqrt(N) * returns.mean() / (returns.std() + 0.01)

df_optim = pd.DataFrame()
df_optim['p1'] = 0
df_optim['Sharpe_Ratio'] = 0
df_optim['rez'] = 0

p1 = 50
tax = -0.05


for p1 in range(1, 100):
    rez = strategy(twitter1, p1, tax)
    sharpe_ratio = Sharpe_Ratio(rez)
    df_optim = df_optim.append({'p1': p1,'Sharpe_Ratio': sharpe_ratio, 'rez': rez.copy()}, ignore_index=True)

df_optim['Sharpe_Ratio'] = df_optim['Sharpe_Ratio'].astype(float)

idx_max = df_optim['Sharpe_Ratio'].idxmax()


p23_strategija = strategy(twitter,  23, tax)

gross_profit = np.cumsum(p23_strategija)
ax[1].plot(gross_profit)


"""
p1 = 20
p2 = 70

df1 = data['Close'].copy()
df = df1.to_frame()
df.columns = ['Close']
price_column_name = 'Close'
taxes = -0.3


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


def Sharpe_Ratio(returns, N=252):
    return np.sqrt(N) * returns.mean() / returns.std()

df_optim = pd.DataFrame(columns=['p1', 'p2', 'Sharpe_Ratio', 'results'])

for p1 in range(1, 100, 2):
    for p2 in range(1, 100, 2):
        if p1 != p2:
            rez = strategy_SMA(df, 'Close', p1,p2, taxes)
            sharpe_ratio = Sharpe_Ratio(rez)
            df_optim = df_optim.append({'p1': p1, 'p2': p2, 'sharpe_ratio': sharpe_ratio, 'rez': rez.copy()}, ignore_index=True)

df_optim['sharpe_ratio'] = df_optim['sharpe_ratio'].astype(float)

idx_max = df_optim['sharpe_ratio'].idxmax()
print('Didziausias Sharpe ratio {} su parametrais p1: {}, p2: {}'.format(df_optim[idx_max]['sharpe_ratio'],
                                                                         df_optim[idx_max]['sharpe_ratio'],
                                                                         df_optim[idx_max]['sharpe_ratio']))

"""