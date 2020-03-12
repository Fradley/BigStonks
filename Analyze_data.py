import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from random import randint
from tqdm import tqdm

#logisitic functions
def merge_tables(path):
    tables = list()
    for f in os.scandir(path):
        if f.is_file():
            tables.append(pd.read_csv(f))
    return pd.concat(tables, axis=0)

def load_symbol(symbol):
    symbol = symbol.lower()
    path = os.path.abspath(symbol)
    
    daily = merge_tables(os.path.join(path, f'{symbol}_daily'))
    intraday = merge_tables(os.path.join(path, f'{symbol}_intraday'))
    sentiment = merge_tables(os.path.join(path, f'{symbol}_sentiment'))
    
    return daily, intraday, sentiment
	
#math functions
def sma(df, metric, n):
    return df[metric].rolling(window=n).mean()

def ema(df, metric, n):
    return df[metric].ewm(span=n, adjust=False).mean()

def typical_price(df, metrics):
    return df[metrics].mean(axis=1)

def moving_standard_dev(df, metric, n):
    return df[metric].rolling(n).std()

def bollinger_bands(df, metric, n, n_dev, avg_func):
    ma = avg_func(df[[metric]], metric, n)
    stdev = moving_standard_dev(df[[metric]], metric, n)
    up_b_band = ma + (n_dev * stdev)
    down_b_band = ma - (n_dev * stdev)
    
    up_b_band.name = f'up_band_{n}'
    down_b_band.name = f'down_band_{n}'
    
    return pd.concat([up_b_band, down_b_band], axis=1)
    
def diff(df, metrics):
    assert(len(metrics) == 2)
    dif = df[metrics[0]] - df[metrics[1]]
    return dif
	
def get_stats(df_in):
	df = df_in.copy()
	df['TP'] = typical_price(df, ['High', 'Low', 'Close'])
	bands = bollinger_bands(df, 'TP', 20, 2, sma)

	df['Upper_Bollinger_Band'] = bands['up_band_20']
	df['Lower_Bollinger_Band'] = bands['down_band_20']

	df['Width'] = diff(df, ['Upper_Bollinger_Band', 'Lower_Bollinger_Band'])

	df['SMA_50'] = sma(df, 'TP', 50)
	df['SMA_200'] = sma(df, 'TP', 200)

	df['EMA_50'] = ema(df, 'TP', 50)
	df['EMA_200'] = ema(df, 'TP', 200)

	df['pct_return'] = df['Close'].pct_change(-1)
	df['cum_return'] = df['pct_return'].cumsum()
	
	return df


def main():
	os.chdir('Data')
	folders = {f.path[2:]: f.path for f in os.scandir() if f.is_dir()}
	symbols = list(folders.keys())
	output = 'C:/Users/silas/Notebooks/BigStonks/Augmented_Data/'
	
	for symbol in tqdm(symbols):
		try:
			day, intra, sntmt = load_symbol(symbol)
			day.sort_values('Time', ascending=True, inplace=True)
			day.reset_index(inplace=True, drop=True)
			day.drop_duplicates('Time', inplace=True)
			
			intra.sort_values('Time', ascending=True, inplace=True)
			intra.reset_index(inplace=True, drop=True)
			intra.drop_duplicates('Time', inplace=True)
			
			day = get_stats(day)
			intra = get_stats(intra)
			
			sntmt = sntmt.groupby('time').mean()
			df = day.merge(sntmt, how='left', left_on='Time', right_index=True)
			df.fillna(0, inplace=True)
			
			df.to_csv(output + f'{symbol}_daily.csv', index=False)
			intra.to_csv(output + f'{symbol}_intraday.csv', index=False)
			
		except:
			print(f'Failed: {symbol}')

if __name__ == '__main__':
	main()
