# TCC-2025
Repositório ao  TCC - ANÁLISE E DESENVOLVIMENTO DE SISTEMAS PARA COMBATE E DETECÇÃO DE FAKE NEWS NA INTERNET

Este é um projeto de detecção de notícias falsas (fake news) que utiliza aprendizado de máquina para classificar textos como verdadeiros ou falsos.

## Estrutura do projeto

O projeto é composto por três principais arquivos:

1. **app.py**: Interface gráfica do detector de fake news
2. **validar_noticias.py**: Script para validar notícias em lote
3. **feedback.py**: Sistema para coletar feedback quando o modelo erra

## Requisitos

>[!IMPORTANT]
>- Python 3.6+ instalado 
>- Gradio
>- Pandas
>- Scikit-learn
>- Joblib
>- Sistemas compatíveis: Windows, macOS e Linux

##  Instalação

Para instalar todas as dependências necessárias:

```
pip install -r requirements.txt
```
O arquivo requirements.txt contém:
```
gradio>=3.50.0
pandas>=1.5.0
scikit-learn>=1.0.0
joblib>=1.1.0
numpy>=1.20.0
regex>=2022.1.18
```

##  Componentes

### Interface Web (app.py)

Este arquivo implementa uma interface web usando Gradio que permite aos usuários inserir textos de notícias e obter classificações em tempo real.

```
import gradio as gr
import joblib

model = joblib.load('fake_news_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

def predict(text):
    text_clean = re.sub(r'[^\w\s]', '', text.lower())
    X = vectorizer.transform([text_clean])
    return model.predict(X)[0]

interface = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(lines=3, placeholder="Cole a notícia aqui..."),
    outputs="label",
    title="Detector de Fake News"
)

interface.launch()
```

### Validação de Notícias (validar_noticias.py)

Este script permite validar várias notícias em lote, útil para testar o desempenho do modelo com novos dados.

```
import joblib
import re
import pandas as pd

# Pré-processa e classifica notícias de teste
for noticia in noticias_teste:
    noticia_limpa = clean_text(noticia)
    noticia_vetorizada = vectorizer.transform([noticia_limpa])
    predicao = model.predict(noticia_vetorizada)[0]
    print(f"Notícia: '{noticia[:50]}...' → Classificação: {predicao}")
```

### Sistema de Feedback (feedback.py)

Este componente permite coletar dados quando o modelo faz previsões incorretas, armazenando-os para futuros retreinamentos do modelo.

```
def add_feedback(text, true_label):
    # Adiciona casos mal classificados a um CSV
    try:
        df = pd.read_csv(feedback_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['text', 'label'])
    
    new_data = pd.DataFrame([[text, true_label]], columns=['text', 'label'])
    df = pd.concat([df, new_data])
    df.to_csv(feedback_file, index=False)
```

## Arquivos de Modelo

O projeto utiliza dois arquivos pré-treinados (que devem estar no diretório do projeto):

- fake_news_model.pkl: O modelo de classificação treinado
- tfidf_vectorizer.pkl: O vetorizador TF-IDF para transformar texto em vetores

## Como Usar

### Interface Web

1 .Execute python **app.py** 

2. Acesse a interface web (normalmente em http://localhost:7860) 

3. Cole o texto da notícia a ser analisada

4. O sistema retornará a classificação (FAKE ou REAL)

### Validação em Lote

1. Edite o arquivo **validar_noticias.py** para incluir suas notícias de teste
2. Execute python **validar_noticias.py**
3. Verifique os resultados no console

### Feedback para Melhorias

1. Quando identificar classificações incorretas, use a função **add_feedback**
2. Exemplo: add_feedback **("Texto da notícia mal classificada", "FAKE")**
3. Os dados são salvos em **feedback_data.csv** para futuros retreinamentos
