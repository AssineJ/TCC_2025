from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from .news_collector import run_collector
from .fake_news_detector import check_news
from .database import init_db, get_db_connection
import os

app = FastAPI(title="Fake News Detector BR", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewsRequest(BaseModel):
    title: str
    content: str

class NewsResponse(BaseModel):
    verdict: str
    probability: float
    message: str

@app.on_event("startup")
async def startup_event():
    init_db()
    print("Banco de dados inicializado")

@app.get("/")
async def root():
    return {"message": "Fake News Detector API - Brasil"}

@app.post("/check-news", response_model=NewsResponse)
async def check_news_endpoint(request: NewsRequest):
    try:
        verdict, probability = check_news(request.title, request.content)
        
        # Mensagem personalizada baseada no veredito
        messages = {
            "VERDADEIRO": "Esta notícia parece ser confiável.",
            "INDETERMINADO": "Não é possível determinar a veracidade com certeza. Consulte fontes adicionais.",
            "PROVAVELMENTE FALSO": "Cuidado! Esta notícia pode conter informações falsas."
        }
        
        return NewsResponse(
            verdict=verdict,
            probability=probability,
            message=messages.get(verdict, "Verifique com fontes confiáveis.")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect-news")
async def collect_news():
    try:
        count = run_collector()
        return {"message": f"Coleta concluída. {count} notícias coletadas."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent-news")
async def get_recent_news(limit: int = 10):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, source_name, source_url, publish_date 
            FROM news_articles 
            ORDER BY collected_date DESC 
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        cursor.close()
        conn.close()
        
        return {"news": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)