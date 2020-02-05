import pandas as pd
import requests
import json
import os
from datetime import datetime
import feedparser
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import re

def get_intraday(symbol):
    now = datetime.now()
    spath = os.path.abspath(f'Data/{symbol}')
    if not os.path.isdir(spath):
        os.mkdir(spath)
    path = os.path.abspath(f'Data/{symbol}/{symbol}_intraday')
    if not os.path.isdir(path):
        os.mkdir(path)
    
    with open('Key') as f:
        key = f.read()
        
    interval = '1min'
    counter = 0
    api_call = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize=full&apikey={key}'
    while counter < 4:
        try:
            req = requests.get(api_call)
            break
        except Exception as e:
            os.sleep(3)
            counter += 1

    amd_ts = json.loads(req.text)
    meta = amd_ts['Meta Data']
    data = amd_ts['Time Series (1min)']

    amd_df = pd.DataFrame(data).T
    col_name = {'1. open': 'Open', '2. high': 'High', '3. low':'Low', '4. close': 'Close', '5. volume': 'Volume', 'index': 'Time'}
    amd_df = amd_df.reset_index()
    amd_df = amd_df.rename(columns=col_name)

    amd_df.to_csv(os.path.join(path, f'{symbol}_intraday_{now.year}_{now.month}_{now.day}.csv'))

def get_daily(symbol):
    now = datetime.now()
    spath = os.path.abspath(f'Data/{symbol}')
    if not os.path.isdir(spath):
        os.mkdir(spath)
    path = os.path.abspath(f'Data/{symbol}/{symbol}_daily')
    if not os.path.isdir(path):
        os.mkdir(path)
    
    with open('Key') as f:
        key = f.read()
        
    interval = '1min'
    counter = 0
    api_call = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    while counter < 4:
        try:
            req = requests.get(api_call)
            break
        except Exception as e:
            os.sleep(3)
            counter += 1

    amd_ts = json.loads(req.text)
    meta = amd_ts['Meta Data']
    data = amd_ts['Time Series (Daily)']

    amd_df = pd.DataFrame(data).T
    col_name = {'1. open': 'Open', '2. high': 'High', '3. low':'Low', '4. close': 'Close', '5. volume': 'Volume', 'index': 'Time'}
    amd_df = amd_df.reset_index()
    amd_df = amd_df.rename(columns=col_name)

    amd_df.to_csv(os.path.join(path, f'{symbol}_daily_{now.year}_{now.month}_{now.day}.csv'))


def strip_html(text):
    tag = re.compile(r'<[^>]+>')
    return tag.sub('', text)

def get_rss(symbol):
    spath = os.path.abspath(f'Data/{symbol}')
    if not os.path.isdir(spath):
        os.mkdir(spath)
    path = os.path.abspath(f'Data/{symbol}/{symbol}_sentiment')
    if not os.path.isdir(path):
        os.mkdir(path)
    feed = f'https://www.nasdaq.com/feed/rssoutbound?symbol={symbol}'

    rss = feedparser.parse(feed)

    articles = rss.entries

    summaries = list()
    for article in articles:
        entry = dict()
        text = strip_html(article['summary']).replace('\n', '')
        if len(text) > 65:
            entry['text'] = text
            entry['time'] = article['published']
            entry['symbols'] = article['nasdaq_tickers'].split(',')
            summaries.append(entry)

    sia = SIA()
    sentiments = list()
    for summary in summaries:
        score = sia.polarity_scores(summary['text'])
        score['text'] = summary['text']
        time = ' '.join(summary['time'].split(' ')[1:4])
        score['time'] = datetime.strptime(time, '%d %b %Y')
        score['tickers'] = summary['symbols']
        sentiments.append(score)

    sentiment_df = pd.DataFrame.from_records(sentiments)
    now = datetime.now()
    sentiment_df.to_csv(os.path.join(path, f'{symbol}_sentiment_{now.year}_{now.month}_{now.day}.csv'))
