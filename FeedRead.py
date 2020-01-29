import requests
from bs4 import BeautifulSoup
import feedparser
import pandas as pd
import time
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import re
import os
from datetime import datetime

def strip_html(text):
	tag = re.compile(r'<[^>]+>')
	return tag.sub('', text)

def get_rss(ticker):
	feed = f'https://www.nasdaq.com/feed/rssoutbound?symbol={ticker}'

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
	return sentiment_df
    
def main():
	path = os.path.abspath('sentiments/AMD/')
	df = get_rss('AMD')
	now = datetime.now()
	df.to_csv(os.path.join(path, f'AMD_sentiment_{now.year}_{now.month}_{now.day}.csv'))


if __name__ == '__main__':
	main()
