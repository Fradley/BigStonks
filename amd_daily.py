import pandas as pd
import requests
import json
import os
from datetime import datetime
import smtplib

# server = smtplib.SMTP('smtp.gmail.com', 587)
# server.connect("smtp.gmail.com",587)
# server.ehlo()
# server.starttls()
# server.ehlo()
# email_user = 'stonkman9001'
# pw = 'WallStreetBets'
# server.login(email_user, pw)

now = datetime.now()

path = os.path.abspath('amd_daily/')
key = '*'
symbol = 'AMD'
interval = '1min'
counter = 0
api_call = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize=full&apikey={key}'
while counter <= 10:
    try:
        req = requests.get(api_call)
        break
    except Exception as e:
        os.sleep(3)
        counter += 1
# if counter == 11:
    # msg = f'\nThe AMD daily data failed to download.\n{e}\n-Stonkman'
# else:
    # msg = f'\nThe AMD Daily File downloaded successfully!\n-Stonkman'
# server.sendmail(email_user + '@gmail.com', 'sfradley96@gmail.com', msg)

amd_ts = json.loads(req.text)
meta = amd_ts['Meta Data']
data = amd_ts['Time Series (1min)']

amd_df = pd.DataFrame(data).T
col_name = {'1. open': 'Open', '2. high': 'High', '3. low':'Low', '4. close': 'Close', '5. volume': 'Volume', 'index': 'Time'}
amd_df = amd_df.reset_index()
amd_df = amd_df.rename(columns=col_name)

amd_df.to_csv(os.path.join(path, f'amd_daily_{now.year}_{now.month}_{now.day}.csv'))