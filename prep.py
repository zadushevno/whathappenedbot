import requests
from pprint import pprint

import pandas as pd

from bs4 import BeautifulSoup
import re


session = requests.session()
news_data = pd.DataFrame(columns=['heading'])

#функция для парсинга страницы интерфакса
def get_news_interfax(page_number, day, month):
    url = f'https://www.interfax.ru/news/2022/{month}/{day}/all/page_{page_number}'
    req = session.get(url)
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')
    news = soup.find_all('div', {'data-id' : True})
    for n in news:
        try:
            news_data.loc[len(news_data.index)] = [n.find('a').text]
        except Exception as e:
            print(e)

from tqdm.auto import tqdm

#скачиваем все новости от определенного дня
def run_all(day, month, year=2022):
    url = f'https://www.interfax.ru/news/{year}/{month}/{day}/all/'
    req = session.get(url)
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')
    n_pages = len(soup.find('div', {'class' : 'pages'}).find_all('a')) #смотрим, сколько страниц с новостями есть для конкретного дня
    for i in range(n_pages+1):
        get_news_interfax(i, day, month)

days_per_month = [31, 28, 30]

#скачиваем новости с января по март
for month in tqdm(range(3)):
    for day in range(days_per_month[month]):
        run_all(day, month + 1)

#функция для парсинга страницы mk.ru
def get_news_mk(day, month):
    url = f'https://www.mk.ru/news/2022/{month}/{day}/'
    req = session.get(url)
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')
    news = soup.find_all('h3', {'class' : 'news-listing__item-title'})
    for n in news:
        try:
            news_data.loc[len(news_data.index)] = [n.text]
        except Exception as e:
            print(e)

#скачиваем новости с января по март
for month in tqdm(range(3)):
    for day in range(days_per_month[month]):
        get_news_mk(day, month + 1)

#записываем в текстовый файл все заголовки
with open('titles.txt', 'w', encoding="utf-8") as f:
    for n in news_data['heading'].to_list():
        print(n, '.', file=f, sep='')

from nltk.tokenize import wordpunct_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import pymorphy2

nltk.download("stopwords")

stops = set(stopwords.words('russian') + ['это', 'весь', 'который', 'мочь', 'свой'])

morph = pymorphy2.MorphAnalyzer()

def lemmatize(x):
    if type(x) != str:
        return ""
    text = wordpunct_tokenize(x)
    result = []
    for word in text:
        if word.isalpha():
            nf = morph.parse(word)[0].normal_form 
            if nf not in stops:
                result.append(nf)
    return " ".join(result)

news_data['lemmatized'] = news_data['heading'].apply(lemmatize)

with open('lemmas.txt', 'w', encoding="utf-8") as f:
    for n in news_data['lemmatized'].to_list():
        print(n, file=f)