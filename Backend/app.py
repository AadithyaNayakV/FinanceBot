from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from fin import llm

app = FastAPI()

@app.post("/chat/")
async def chat(query: str = Form(...), files: List[UploadFile] = File(None)):
    
    res = llm(query=query, files=files)
    return {"answer": res}
