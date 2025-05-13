import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.utils import shuffle
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib

# Carrega os datasets
fake = pd.read_csv('Fake.csv')
real = pd.read_csv('True.csv')

# Verifica as colunas (opcional, só para debug)
print("Colunas no Fake.csv:", fake.columns)
print("Colunas no True.csv:", real.columns)

# Adiciona rótulos
fake['label'] = 'FAKE'
real['label'] = 'REAL'

# Combina os datasets e seleciona apenas 'text' e 'label'
df = pd.concat([fake, real])
df = df[['text', 'label']]  # Se a coluna de texto for 'text'

# Pré-processamento opcional (limpeza de texto)
import re
def clean_text(text):
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^\w\s]', '', text)   # Remove pontuação
    return text.strip().lower()            # Padroniza para minúsculas

df['text'] = df['text'].apply(clean_text)

# Divide os dados
X = df['text']
y = df['label']

# Vetorização TF-IDF
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
X_tfidf = vectorizer.fit_transform(X)

# Separa em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# Treina o modelo
model = PassiveAggressiveClassifier(max_iter=1000)
model.fit(X_train, y_train)

# Avaliação
y_pred = model.predict(X_test)
print("\nAcurácia:", accuracy_score(y_test, y_pred))
print("Matriz de Confusão:\n", confusion_matrix(y_test, y_pred, labels=['FAKE', 'REAL']))

joblib.dump(model, 'fake_news_model.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
print("Modelo e vetorizador salvos!")

def update_model():
    # Carrega dados originais + feedback
    df_original = pd.concat([pd.read_csv('Fake.csv'), pd.read_csv('True.csv')])
    df_feedback = pd.read_csv('feedback_data.csv')
    
    # Combina e embaralha os dados
    df_updated = pd.concat([df_original, df_feedback])
    df_updated = shuffle(df_updated)
    
    # Retreina o modelo (reutilize o código existente de treino)
    X = vectorizer.transform(df_updated['text'])
    model.partial_fit(X, df_updated['label'])
    
    # Salva o novo modelo
    joblib.dump(model, 'fake_news_model_v2.pkl')

# Execute manualmente quando tiver novos feedbacks
# update_model()

def enhanced_features(text):
    return [
        sum(1 for c in text if c.isupper()),  # num_uppercase
        text.count('!'),                      # num_exclamations
        int('http' in text)                   # has_http
    ]

# Cria lista de features
features_list = df['text'].apply(enhanced_features).tolist()

# Cria DataFrame com as features
features_df = pd.DataFrame(
    features_list,
    columns=['num_uppercase', 'num_exclamations', 'has_http']
)

# Combina com o DataFrame original
df = pd.concat([df.reset_index(drop=True), features_df.reset_index(drop=True)], axis=1)

print("\nColunas do DataFrame:", df.columns.tolist())
print("\nPrimeiras linhas:")
print(df[['text', 'num_uppercase', 'num_exclamations', 'has_http']].head())


