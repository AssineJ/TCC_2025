import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import re
import joblib
from .database import get_db_connection
import os

class FakeNewsDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='portuguese')
        self.model = LogisticRegression(max_iter=1000, random_state=42)
        self.is_trained = False
        
    def clean_text(self, text):
        if not text:
            return ""
        # Converter para minúsculas
        text = text.lower()
        # Remover caracteres especiais e números
        text = re.sub(r'[^a-záàâãéèêíïóôõöúçñ\s]', '', text)
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def prepare_data(self):
        # Carregar dados do banco SQLite
        conn = get_db_connection()
        
        # Buscar notícias já classificadas
        query = """
        SELECT title, content, is_fake, verification_score 
        FROM news_articles 
        WHERE is_fake IS NOT NULL AND LENGTH(content) > 100
        """
        
        data = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(data) == 0:
            # Se não houver dados, usar exemplos básicos
            return self.create_sample_data()
        
        # Limpar texto
        data['clean_text'] = data['title'] + ' ' + data['content']
        data['clean_text'] = data['clean_text'].apply(self.clean_text)
        
        return data

    def create_sample_data(self):
        # Dados de exemplo para treinamento inicial
        sample_data = {
            'title': [
                'Vacinação contra COVID-19 avança no Brasil',
                'Economia brasileira cresce 1,2% no último trimestre',
                'Novo programa de incentivo à energia solar',
                'Vacina causa magnetismo em braços',
                'Governo distribuirá R$ 1000 para todos',
                'Comida de McDonald´s é feita de minhocas'
            ],
            'content': [
                'Ministério da Saúde anunciou que mais de 70% da população recebeu vacina',
                'IBGE registrou crescimento de 1,2% no último trimestre',
                'Governo anunciou programa de incentivo à energia solar em residências',
                'Estudo comprova que vacinados desenvolvem magnetismo nos braços',
                'Presidente anunciou auxílio de R$ 1000 para todos os brasileiros',
                'Investigação revela que carne do McDonald´s é feita de minhocas'
            ],
            'is_fake': [False, False, False, True, True, True],
            'verification_score': [0.1, 0.2, 0.15, 0.9, 0.85, 0.95]
        }
        
        data = pd.DataFrame(sample_data)
        data['clean_text'] = data['title'] + ' ' + data['content']
        data['clean_text'] = data['clean_text'].apply(self.clean_text)
        
        return data

    def train(self):
        print("Preparando dados para treinamento...")
        data = self.prepare_data()
        
        if len(data) < 10:
            print("Dados insuficientes para treinamento.")
            return False
        
        # Vetorizar texto
        X = self.vectorizer.fit_transform(data['clean_text'])
        y = data['is_fake'].values
        
        # Dividir em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Treinar modelo
        print("Treinando modelo...")
        self.model.fit(X_train, y_train)
        
        # Avaliar
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Acurácia do modelo: {accuracy:.2f}")
        print(classification_report(y_test, y_pred))
        
        self.is_trained = True
        
        # Salvar modelo
        self.save_model()
        return True

    def predict(self, title, content):
        if not self.is_trained:
            self.load_model()
            
        text = self.clean_text(title + ' ' + content)
        if not text:
            return 0.5  # Probabilidade neutra se não há texto
        
        X = self.vectorizer.transform([text])
        proba = self.model.predict_proba(X)[0]
        
        # Retornar probabilidade de ser fake news
        return proba[1] if len(proba) > 1 else 0.5

    def save_model(self):
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model
        }
        # Criar diretório se não existir
        os.makedirs('models', exist_ok=True)
        joblib.dump(model_data, 'models/fake_news_model.pkl')
        print("Modelo salvo com sucesso.")

    def load_model(self):
        try:
            if os.path.exists('models/fake_news_model.pkl'):
                model_data = joblib.load('models/fake_news_model.pkl')
                self.vectorizer = model_data['vectorizer']
                self.model = model_data['model']
                self.is_trained = True
                print("Modelo carregado com sucesso.")
            else:
                print("Arquivo de modelo não encontrado. Treinando novo modelo...")
                self.train()
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}. Treinando novo modelo...")
            self.train()

def check_news(title, content):
    detector = FakeNewsDetector()
    detector.load_model()
    probability = detector.predict(title, content)
    
    # Classificar com base na probabilidade
    if probability < 0.3:
        return "VERDADEIRO", probability
    elif probability < 0.7:
        return "INDETERMINADO", probability
    else:
        return "PROVAVELMENTE FALSO", probability