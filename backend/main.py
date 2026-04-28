import os
import shutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from db_builder import load_file_to_db, DATA_DIR, rebuild_database
from agent import query_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load initial data from the data folder
    rebuild_database()
    yield

app = FastAPI(title="SQL Chatbot API", lifespan=lifespan)

# Enable CORS for frontend hosting (GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


@app.get("/init")
async def initialize():
    # Sync database with data/ folder and CLEAN UP all temp tables
    rebuild_database(clean_temp=True)
    
    # Generate summary
    summary = query_agent("Please list the tables present in the database and provide a brief summary of the data in each table.")
    return {"summary": summary}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = query_agent(request.message)
    return ChatResponse(response=response)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Temporary location for ingestion
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_uploads")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save file temporarily
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Ingest into database as a temporary table
        success, message = load_file_to_db(file_path, is_temp=True)
        
        # Always remove the physical temp file after DB ingestion
        if os.path.exists(file_path):
            os.remove(file_path)
            
        if not success:
            raise HTTPException(status_code=400, detail=message)
            
        return {"message": f"Temporary table created: {message}. It will be deleted when you refresh the page."}
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
