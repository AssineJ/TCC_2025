import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# Carrega os datasets
fake = pd.read_csv('Fake.csv')
real = pd.read_csv('True.csv')

# Adiciona rótulos
fake['label'] = 'FAKE'
real['label'] = 'REAL'

# Junta os dois em um só
df = pd.concat([fake, real])
df = df[['text', 'label']]  
# usa só o texto e o rótulo

# Divide os dados
X = df['text']
y = df['label']

# Pré-processamento: Vetorização TF-IDF
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
X_tfidf = vectorizer.fit_transform(X)

# Treinamento e teste
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# Cria o modelo
model = PassiveAggressiveClassifier(max_iter=1000)
model.fit(X_train, y_train)

# Testa
y_pred = model.predict(X_test)
print("Acurácia:", accuracy_score(y_test, y_pred))
print("Matriz de confusão:\n", confusion_matrix(y_test, y_pred))
