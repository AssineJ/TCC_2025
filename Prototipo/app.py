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