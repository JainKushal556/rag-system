from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI , HTTPException , status
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from pathlib import Path
from Ingestion_Pipeline.textloader import filetotext
from Ingestion_Pipeline.chunking import chunker
from Query_Pipeline.query_embedder import generate_query_embeddings
from Query_Pipeline.chunk_retriver import chunk_retriver
from Query_Pipeline.llm_answer import generate_answer
from backend.utilities import format_size
from datetime import datetime
import shutil
import os
import time




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/files")
def read_files():
    folder = Path("backend/uploaded_files")
    if not folder.exists():
        return []
    files_list = []
    
    for f in folder.iterdir():
        if f.is_file():
            file_stat = f.stat()
            created_time = datetime.fromtimestamp(file_stat.st_ctime).strftime("%d %b %Y, %I:%M %p")
            
            files_list.append({
                "name": f.name,
                "size": format_size(file_stat.st_size),
                "raw_size_bytes": file_stat.st_size,
                "added_date": created_time
            })
            
    return files_list

@app.post("/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    start_time = time.time()
    if file is None or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded! Please select a file."
        )
    
    directory_path = Path("backend/uploaded_files")
    directory_path.mkdir(exist_ok=True)

    final_path = os.path.join(directory_path,file.filename)
    with open(final_path,"wb") as destination:
        shutil.copyfileobj(file.file,destination)
        
    if filetotext(final_path):
        await chunker()
    else:
        end_time = time.time()
        elapsed_time = end_time - start_time
        return {
            "status": "UnSuccessful",
            "filename": file.filename,
            "filetype":file.content_type,
            "file_path":final_path,
            "time_taken": elapsed_time,
        }
    end_time = time.time()
    elapsed_time = end_time - start_time
    return {
        "status": "Success",
        "filename": file.filename,
        "filetype":file.content_type,
        "file_path":final_path,
        "time_taken": elapsed_time
    }

@app.post("/query")
async def user_query(query : str):
    if not query or not isinstance(query, str) or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty! Please provide a valid question."
        )
    start_time = time.time()
    embeddings =await generate_query_embeddings(query)
    print(f"Generated embeddings for query: {embeddings}")
    retrived_chunks = chunk_retriver(embeddings)
    print(f"Retrieved chunks: {retrived_chunks}")
    generated_answer = await generate_answer(query, retrived_chunks)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return {
        "query": query, 
        "answer": generated_answer,
        "time_taken": elapsed_time
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}


# uvicorn backend.main:app --reload