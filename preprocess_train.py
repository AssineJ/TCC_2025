# preprocess_train.py
# Carrega datasets públicos (ex: CSV do Kaggle ou LIAR) e prepara train/test
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib


DATA_CSV = 'articles.csv' # arquivo gerado com data_collection.py ou datasets baixados
VECTORIZER_PATH = 'models/tfidf_vectorizer.joblib'
TRAIN_PATH = 'models/train_data.joblib'


os.makedirs('models', exist_ok=True)


def load_csv(path=DATA_CSV):
df = pd.read_csv(path)
# Se não houver coluna label, precisa rotular manualmente (0 = real, 1 = fake)
return df


def basic_clean(text):
if pd.isna(text):
return ''
return str(text)


if __name__ == '__main__':
df = load_csv()
# Exemplo: se você tiver duas colunas title e content, combina-las
df['text'] = (df.get('title','') + ' ' + df.get('content','')).fillna('')


# **IMPORTANTE**: para treinar, você precisa de labels. Exemplo: se você tiver 'label' na tabela
if 'label' not in df.columns:
print('Nenhuma coluna label encontrada. Coloque labels manualmente em articles.csv (0 real / 1 fake)')
df.to_csv('to_label.csv', index=False)
raise SystemExit


X = df['text']
y = df['label']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1,2))
X_train_tfidf = vectorizer.fit_transform(X_train)


joblib.dump(vectorizer, VECTORIZER_PATH)
joblib.dump((X_train_tfidf, X_test, y_train, y_test), TRAIN_PATH)
print('Preprocess done. Vectorizer and train data saved in models/')