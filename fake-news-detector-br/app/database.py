import sqlite3
import pandas as pd
import os
from datetime import datetime

def get_db_connection():
    # Usar caminho absoluto para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'news.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de notícias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        source_url TEXT NOT NULL,
        source_name TEXT NOT NULL,
        publish_date TIMESTAMP,
        collected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_verified BOOLEAN DEFAULT FALSE,
        is_fake BOOLEAN,
        verification_score REAL
    )
    ''')
    
    # Tabela de fontes confiáveis
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trusted_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        reliability_score REAL DEFAULT 1.0,
        category TEXT
    )
    ''')
    
    # Inserir fontes confiáveis brasileiras
    trusted_sources = [
        ('g1.globo.com', 'G1', 0.95, 'geral'),
        ('folha.uol.com.br', 'Folha de S.Paulo', 0.93, 'geral'),
        ('estadao.com.br', 'Estadão', 0.92, 'geral'),
        ('uol.com.br', 'UOL', 0.90, 'geral'),
        ('bbc.com/portuguese', 'BBC News Brasil', 0.96, 'internacional'),
        ('cnnbrasil.com.br', 'CNN Brasil', 0.91, 'geral'),
        ('nexojornal.com.br', 'Nexo Jornal', 0.94, 'analise'),
        ('piaui.folha.uol.com.br', 'Piauí', 0.93, 'revista'),
        ('agenciaBrasil.ebc.com.br', 'Agência Brasil', 0.92, 'governo'),
        ('brasil.elpais.com', 'El País Brasil', 0.91, 'internacional')
    ]
    
    for domain, name, score, category in trusted_sources:
        cursor.execute(
            'INSERT OR IGNORE INTO trusted_sources (domain, name, reliability_score, category) VALUES (?, ?, ?, ?)',
            (domain, name, score, category)
        )
    
    conn.commit()
    
    # Verificar se precisamos adicionar dados de exemplo
    cursor.execute('SELECT COUNT(*) as count FROM news_articles')
    if cursor.fetchone()['count'] == 0:
        add_sample_data(cursor)
    
    conn.commit()
    cursor.close()
    conn.close()

def add_sample_data(cursor):
    """Adiciona dados de exemplo para treinamento inicial"""
    sample_news = [
        # Notícias verdadeiras (exemplos)
        ('Vacinação contra COVID-19 avança no Brasil', 
         'O Ministério da Saúde anunciou que mais de 70% da população brasileira recebeu pelo menos duas doses da vacina contra COVID-19. A campanha de vacinação continua em todo o país para ampliar a cobertura vacinal.',
         'https://exemplo.com/vacinacao', 'G1', datetime.now(), False, 0.1),
         
        ('Economia brasileira cresce 1,2% no último trimestre', 
         'Segundo dados do IBGE, a economia brasileira registrou crescimento de 1,2% no último trimestre, impulsionada principalmente pelo setor de serviços e pela agropecuária.',
         'https://exemplo.com/economia', 'Estadão', datetime.now(), False, 0.2),
         
        ('Novo programa de incentivo à energia solar', 
         'O governo federal anunciou um novo programa de incentivo à geração de energia solar em residências. A iniciativa prevê descontos em equipamentos e linhas de crédito especiais.',
         'https://exemplo.com/energia-solar', 'UOL', datetime.now(), False, 0.15),
         
        # Notícias falsas (exemplos)
        ('Vacina contra COVID-19 causa magnetismo em braços', 
         'Estudo comprova que pessoas vacinadas contra COVID-19 desenvolvem magnetismo, conseguindo segurar objetos metálicos com a pele. Especialistas alertam para este efeito colateral grave.',
         'https://fake.com/magnetismo', 'Site Não Confiável', datetime.now(), True, 0.9),
         
        ('Governo distribuirá R$ 1000 para todos os brasileiros', 
         'O presidente anunciou que todos os brasileiros receberão um auxílio de R$ 1000 mensais permanentemente. O pagamento começará na próxima semana sem necessidade de cadastro.',
         'https://fake.com/auxilio', 'Site Não Confiável', datetime.now(), True, 0.85),
         
        ('Comida de McDonald´s é feita de minhocas processadas', 
         'Investigação revela que a carne utilizada pelo McDonald´s é na verdade minhocas processadas e misturadas com químicos para parecer carne bovina. Empresa nega as acusações.',
         'https://fake.com/mcdonalds', 'Site Não Confiável', datetime.now(), True, 0.95),
    ]
    
    for title, content, url, source, date, is_fake, score in sample_news:
        cursor.execute(
            'INSERT INTO news_articles (title, content, source_url, source_name, publish_date, is_fake, verification_score) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, content, url, source, date, is_fake, score)
        )