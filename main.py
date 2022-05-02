import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'

twitter = pd.read_csv('data/TWTR.csv').set_index('Date')
twitter.index = pd.to_datetime(twitter.index)
twitter.tail()

def SMA(data, window):
    sma = data.rolling(window = window).mean()
    return sma


twitter['SMA_50'] = SMA(twitter['Close'], 50)
twitter['SMA_50'] = twitter['SMA_50'].fillna(0)
twitter.tail()


def Bollinger_Bands(data, sma, window):
    std = data.rolling(window = window).std()
    upper_bb = sma + std * 2
    lower_bb = sma - std * 2
    return upper_bb, lower_bb


twitter['Upper_BB'], twitter['Lower_BB'] = Bollinger_Bands(twitter['Close'], twitter['SMA_50'], 50)
twitter['Upper_BB'] = twitter['Upper_BB'].fillna(0)
twitter['Lower_BB'] = twitter['Lower_BB'].fillna(0)
twitter.tail()

# Plotting
fig, ax = plt.subplots(2, 1, sharex=True, sharey=False)

ax[0].plot(twitter[['Close', 'SMA_50', 'Upper_BB', 'Lower_BB']])
ax[0].legend(['Close', 'SMA_50', 'Upper_BB', 'Lower_BB'])

twitter['Future_Position'] = 0
twitter['Position_Changed'] = False
have_invested = 0

for i in range(len(twitter)):
    if have_invested == 0:
        # Jeigu neturim nusipirke
        if twitter.iloc[i]['Close'] < twitter.iloc[i]['SMA_50'] and twitter.iloc[i]['Close'] > twitter.iloc[i]['Lower_BB']:
            twitter.iloc[i, twitter.columns.get_loc('Future_Position')] = 1
            have_invested = 1
            ax[0].scatter(twitter.index[i], twitter['SMA_50'][i], marker='^', color='green')
        else:
            twitter.iloc[i]['Future_Position'] = 0
    else:
        if twitter.iloc[i]['Close'] > twitter.iloc[i]['Upper_BB']:
            twitter.iloc[i, twitter.columns.get_loc('Position_Changed')] = True
            twitter.iloc[i, twitter.columns.get_loc('Future_Position')] = 0
            have_invested = 0
            ax[0].scatter(twitter.index[i], twitter['Close'][i], marker='v', color='red')
        elif twitter.iloc[i]['Close'] < twitter.iloc[i]['Lower_BB']:
            twitter.iloc[i, twitter.columns.get_loc('Position_Changed')] = True
            twitter.iloc[i, twitter.columns.get_loc('Future_Position')] = 0
            have_invested = 0
            ax[0].scatter(twitter.index[i], twitter['Close'][i], marker='v', color='red')
        else:
            twitter.iloc[i, twitter.columns.get_loc('Future_Position')] = 1

taxes = -0.05
twitter['Taxes'] = twitter['Position_Changed'] * taxes * 1

twitter['Price_Diff'] = twitter['Close'].diff(1)
twitter.iloc[0, twitter.columns.get_loc('Price_Diff')] = 0

twitter['Profit_from_Position'] = twitter['Price_Diff'] * twitter['Future_Position']
twitter['Gross_Profit'] = twitter['Profit_from_Position'] + twitter['Taxes']

gross_profit = np.cumsum(twitter['Gross_Profit'])

ax[1].plot(gross_profit, label='Non-optimized profit')

twitter1 = twitter[['Close']].copy()

def strategy(data, window, taxes):
    data['SMA_50'] = SMA(data['Close'], window)
    data['SMA_50'] = data['SMA_50'].fillna(0)
    data.tail()

    data['Upper_BB'], data['Lower_BB'] = Bollinger_Bands(data['Close'], data['SMA_50'], window)
    data['Upper_BB'] = data['Upper_BB'].fillna(0)
    data['Lower_BB'] = data['Lower_BB'].fillna(0)
    data.tail()

    data['Future_Position'] = 0
    data['Position_Changed'] = False
    have_invested = 0

    for i in range(len(data)):
        if have_invested == 0:
        # Jeigu neturim nusipirke
            if data.iloc[i]['Close'] < data.iloc[i]['SMA_50'] and data.iloc[i]['Close'] > data.iloc[i]['Lower_BB']:
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

for p1 in range(1, 100):
    rez = strategy(twitter1, p1, taxes)
    sharpe_ratio = Sharpe_Ratio(rez)
    df_optim = df_optim.append({'p1': p1,'Sharpe_Ratio': sharpe_ratio, 'rez': rez.copy()}, ignore_index=True)

df_optim['Sharpe_Ratio'] = df_optim['Sharpe_Ratio'].astype(float)

idx_max = df_optim['Sharpe_Ratio'].idxmax()

p23_strategija = strategy(twitter,  23, taxes)

gross_profit = np.cumsum(p23_strategija)
ax[1].plot(gross_profit)
ax[1].legend(['Non-optimized', 'optimized'])