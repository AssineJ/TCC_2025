# data_collection.py
# Baixa artigos via NewsAPI (usar API KEY). Salva CSV com colunas: url, title, content, source, publishedAt, image_url
import os
import requests
import csv
from dotenv import load_dotenv


load_dotenv()
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')


def fetch_from_newsapi(query, page=1, page_size=100):
url = 'https://newsapi.org/v2/everything'
params = {
'q': query,
'pageSize': page_size,
'page': page,
'language': 'en',
'sortBy': 'relevancy',
'apiKey': NEWSAPI_KEY
}
r = requests.get(url, params=params)
r.raise_for_status()
return r.json()


def save_articles(articles, out_csv='articles.csv'):
keys = ['url','title','content','source','publishedAt','image_url']
exists = os.path.exists(out_csv)
with open(out_csv, 'a', newline='', encoding='utf-8') as f:
writer = csv.DictWriter(f, fieldnames=keys)
if not exists:
writer.writeheader()
for a in articles:
writer.writerow({
'url': a.get('url'),
'title': a.get('title'),
'content': a.get('content') or a.get('description') or '',
'source': a.get('source',{}).get('name'),
'publishedAt': a.get('publishedAt'),
'image_url': a.get('urlToImage')
})


if __name__ == '__main__':
q = input('Query (ex: politics, covid, Bolsonaro): ')
resp = fetch_from_newsapi(q)
save_articles(resp.get('articles',[]))
print('Saved', len(resp.get('articles',[])), 'articles to articles.csv')