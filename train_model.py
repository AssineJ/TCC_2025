# train_model.py
import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score


os.makedirs('models', exist_ok=True)


VECTORIZER_PATH = 'models/tfidf_vectorizer.joblib'
TRAIN_PATH = 'models/train_data.joblib'
MODEL_PATH = 'models/fakenews_model.joblib'


if __name__ == '__main__':
vectorizer = joblib.load(VECTORIZER_PATH)
X_train_tfidf, X_test_texts, y_train, y_test = joblib.load(TRAIN_PATH)


clf = LogisticRegression(max_iter=1000)
clf.fit(X_train_tfidf, y_train)


# Avaliação simples (usa X_test_texts → vectorize)
X_test_tfidf = vectorizer.transform(X_test_texts)
preds = clf.predict(X_test_tfidf)
print('Accuracy:', accuracy_score(y_test, preds))
print(classification_report(y_test, preds))


joblib.dump(clf, MODEL_PATH)
print('Model saved to', MODEL_PATH)