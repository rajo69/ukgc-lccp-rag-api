from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from rag_engine import UKGC_RAG
import os

# Load environment variables from .env file
load_dotenv()

# Global RAG instance
rag_app = UKGC_RAG()

# Lifecycle manager: Loads the AI model when the server starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up... Loading RAG Index...")
    try:
        rag_app.load_or_create_index()
    except Exception as e:
        print(f"❌ Failed to load index: {e}")
    yield
    print("🛑 Shutting down...")

# Initialize FastAPI
app = FastAPI(title="UKGC LCCP RAG API", lifespan=lifespan)

# --- Pydantic Models (Data Validation) ---
class QueryRequest(BaseModel):
    question: str

class SourceModel(BaseModel):
    condition: str
    context: str
    links: list[str]

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceModel]

# --- Endpoints ---

@app.get("/")
def health_check():
    return {"status": "active", "message": "UKGC RAG API is running"}

@app.post("/chat", response_model=QueryResponse)
def chat_endpoint(request: QueryRequest):
    """
    Send a question to the RAG engine.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = rag_app.query(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # This block allows running directly with `python main.py`
    uvicorn.run(app, host="0.0.0.0", port=8000)