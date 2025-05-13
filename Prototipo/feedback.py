import pandas as pd
import joblib

# Carrega modelo e vetorizador
model = joblib.load('fake_news_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Arquivo para armazenar correções
feedback_file = 'feedback_data.csv'

def add_feedback(text, true_label):
    try:
        df = pd.read_csv(feedback_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['text', 'label'])
    
    new_data = pd.DataFrame([[text, true_label]], columns=['text', 'label'])
    df = pd.concat([df, new_data])
    df.to_csv(feedback_file, index=False)

# Exemplo de uso quando o modelo erra:
texto_mal_classificado = "Vaccines contain microchips to track people"
add_feedback(texto_mal_classificado, 'FAKE')  # Corrige para FAKE