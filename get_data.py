import data_collect as dc
import time
from tqdm import tqdm

symbol_list = ['aapl', 'twtr', 'tsla', 'nflx', 'fb', 'msft', 'nvda', 'ge', 'amd', 'bac']

for symbol in tqdm(symbol_list):
	try:
		dc.get_intraday(symbol)
	except:
		print(f'Intraday for {symbol} failed.') 
	else:
		print(f'Intraday for {symbol} succeeded.') 
		
		
	try:
		dc.get_daily(symbol)
	except:
		print(f'Daily for {symbol} failed.') 
	else:
		print(f'Daily for {symbol} succeeded.') 
		
		
	try:
		dc.get_rss(symbol)
	except:
		print(f'Sentiment for {symbol} failed.') 
	else:
		print(f'Sentiment for {symbol} succeeded.') 
	
	time.sleep(30)
