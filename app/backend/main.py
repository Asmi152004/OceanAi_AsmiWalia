from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import shutil
import os
from dotenv import load_dotenv

load_dotenv()

from .rag import RAGPipeline
from .llm import LLMService
from ..utils.parsers import parse_document

app = FastAPI(title="Autonomous QA Agent Backend")

# Initialize Services
rag = RAGPipeline()
llm_service = LLMService()

class QueryRequest(BaseModel):
    query: str

class ScriptGenRequest(BaseModel):
    test_case: dict
    html_content: str = "" # Optional if we want to pass it directly

@app.get("/")
def read_root():
    return {"status": "QA Agent Backend Running"}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    documents = []
    for file in files:
        content = await file.read()
        text = parse_document(file.filename, content)
        documents.append({"content": text, "source": file.filename})
    
    count = rag.ingest_documents(documents)
    return {"message": f"Successfully ingested {count} chunks from {len(files)} files."}

@app.post("/generate-test-cases")
def generate_test_cases(request: QueryRequest):
    # Retrieve context
    context_docs = rag.retrieve_context(request.query, k=5)
    context_text = "\n\n".join([f"Source: {d.metadata['source']}\nContent: {d.page_content}" for d in context_docs])
    
    # Generate with LLM
    result = llm_service.generate_test_cases(context_text, request.query)
    return result

@app.post("/generate-script")
def generate_script(request: ScriptGenRequest):
    # We might need to retrieve HTML if not passed, but for now assume UI passes it or we find it in context
    # Let's try to find HTML in the vector DB if not provided, or just rely on what was ingested.
    
    # Retrieve context specific to the test case feature to help with rules
    context_docs = rag.retrieve_context(request.test_case.get('feature', ''), k=3)
    context_text = "\n\n".join([f"Source: {d.metadata['source']}\nContent: {d.page_content}" for d in context_docs])
    
    script = llm_service.generate_selenium_script(request.test_case, request.html_content, context_text)
    return {"script": script}

@app.post("/clear-kb")
def clear_knowledge_base():
    rag.clear_db()
    return {"message": "Knowledge Base Cleared"}
