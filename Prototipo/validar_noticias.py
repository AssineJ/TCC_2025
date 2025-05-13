import joblib
import re
import pandas as pd

# Função de limpeza (igual à usada no treino)
def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip().lower()

# Carrega o modelo e o vetorizador
model = joblib.load('fake_news_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Dados externos de exemplo (substitua pelos seus)
noticias_teste = [
    "NASA announces aliens exist!",  # Provavelmente FAKE
    "New law reduces taxes for families",  # Provavelmente REAL
    "Drinking bleach cures COVID-19"  # Provavelmente FAKE
]

# Pré-processa e classifica
for noticia in noticias_teste:
    noticia_limpa = clean_text(noticia)
    noticia_vetorizada = vectorizer.transform([noticia_limpa])
    predicao = model.predict(noticia_vetorizada)[0]
    print(f"Notícia: '{noticia[:50]}...' → Classificação: {predicao}")