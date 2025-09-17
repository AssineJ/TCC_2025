import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
import pandas as pd
from datetime import datetime, timedelta
import time
import re
import os
import feedparser
import random
from .database import get_db_connection

class NewsCollector:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.config = Config()
        self.config.browser_user_agent = self.user_agent
        self.config.request_timeout = 10
        
        # Fontes de notícias brasileiras
        self.news_sources = [
            {
                'name': 'G1',
                'url': 'https://g1.globo.com/',
                'rss': 'https://g1.globo.com/rss/g1/'
            },
            {
                'name': 'UOL',
                'url': 'https://www.uol.com.br/',
                'rss': 'https://rss.uol.com.br/feed/noticias.xml'
            },
            {
                'name': 'Folha de S.Paulo',
                'url': 'https://www.folha.uol.com.br/',
                'rss': 'https://feeds.folha.uol.com.br/emcimadahora/rss091.xml'
            },
            {
                'name': 'Estadão',
                'url': 'https://www.estadao.com.br/',
                'rss': 'https://rss.estadao.com.br/geral.xml'
            },
            {
                'name': 'CNN Brasil',
                'url': 'https://www.cnnbrasil.com.br/',
                'rss': 'https://www.cnnbrasil.com.br/feed/'
            },
            {
                'name': 'BBC Brasil',
                'url': 'https://www.bbc.com/portuguese',
                'rss': 'https://feeds.bbci.co.uk/portuguese/rss.xml'
            }
        ]

    def extract_news_from_rss(self, rss_url, source_name):
        try:
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:10]:  # Limitar a 10 notícias por fonte
                try:
                    # Verificar se a notícia já existe no banco
                    if not self.article_exists(entry.link):
                        article = {
                            'title': entry.title,
                            'url': entry.link,
                            'published': entry.get('published', ''),
                            'source': source_name
                        }
                        articles.append(article)
                except:
                    continue
                    
            return articles
        except Exception as e:
            print(f"Erro ao processar RSS {rss_url}: {e}")
            return []

    def scrape_article_content(self, url):
        try:
            article = Article(url, config=self.config)
            article.download()
            article.parse()
            
            return {
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image
            }
        except Exception as e:
            print(f"Erro ao fazer scraping de {url}: {e}")
            return None

    def article_exists(self, url):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM news_articles WHERE source_url = ?", (url,))
        exists = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return exists

    def collect_news(self):
        all_articles = []
        
        for source in self.news_sources:
            print(f"Coletando notícias de {source['name']}...")
            
            # Coletar do RSS
            rss_articles = self.extract_news_from_rss(source['rss'], source['name'])
            
            for article_info in rss_articles:
                content = self.scrape_article_content(article_info['url'])
                if content and content['text'] and len(content['text']) > 100:  # Garantir conteúdo mínimo
                    article_data = {
                        'title': content['title'],
                        'content': content['text'],
                        'source_url': article_info['url'],
                        'source_name': source['name'],
                        'publish_date': content['publish_date'] or datetime.now(),
                        'collected_date': datetime.now()
                    }
                    all_articles.append(article_data)
            
            # Esperar um tempo aleatório entre requisições
            time.sleep(random.uniform(1, 3))
        
        # Salvar artigos no banco de dados
        self.save_articles_to_db(all_articles)
        return len(all_articles)

    def save_articles_to_db(self, articles):
        if not articles:
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for article in articles:
            try:
                cursor.execute('''
                INSERT INTO news_articles (title, content, source_url, source_name, publish_date, collected_date)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    article['title'][:500],  # Limitar tamanho do título
                    article['content'][:10000],  # Limitar tamanho do conteúdo
                    article['source_url'],
                    article['source_name'],
                    article['publish_date'],
                    article['collected_date']
                ))
            except Exception as e:
                print(f"Erro ao salvar artigo: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Salvos {len(articles)} artigos no banco de dados")

def run_collector():
    collector = NewsCollector()
    count = collector.collect_news()
    print(f"Coleta concluída. {count} novas notícias coletadas.")
    return count